import os
import subprocess
import tempfile
from flask import Flask, request, send_file
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB limit

@app.route("/")
def index():
    return "✅ Video Converter Backend is running!"

@app.route("/convert", methods=["POST"])
def convert():
    uploaded_file = request.files.get("file")
    to_format = request.form.get("to_format", "").lower()

    if not uploaded_file or uploaded_file.filename == '':
        return "No file uploaded", 400

    allowed_formats = ["mp4", "mkv", "webm"]
    if to_format not in allowed_formats:
        return f"Unsupported format: {to_format}", 400

    with tempfile.TemporaryDirectory() as tmpdir:
        input_filename = secure_filename(uploaded_file.filename)
        input_path = os.path.join(tmpdir, input_filename)
        uploaded_file.save(input_path)

        name_wo_ext = os.path.splitext(input_filename)[0]
        output_filename = f"{name_wo_ext}.{to_format}"
        output_path = os.path.join(tmpdir, output_filename)

        # Build FFMPEG command
        if to_format == "webm":
            cmd = [
                "ffmpeg", "-i", input_path,
                "-c:v", "libvpx-vp9",
                "-c:a", "libopus",
                "-y",  # overwrite
                output_path
            ]
        else:
            cmd = [
                "ffmpeg", "-i", input_path,
                "-c:v", "libx264",
                "-c:a", "aac",
                "-y",  # overwrite
                output_path
            ]

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=120  # 2 min max
            )

            if result.returncode != 0:
                print("FFMPEG error:", result.stderr.decode())
                return "Conversion failed", 500

            return send_file(output_path, as_attachment=True)

        except subprocess.TimeoutExpired:
            return "Conversion timed out", 500
        except Exception as e:
            return f"Internal server error: {e}", 500

# Do not run app.run() in production — Gunicorn will run it
