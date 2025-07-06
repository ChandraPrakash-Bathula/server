import os
import subprocess
import tempfile
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

# ======================
# 1️⃣ Create Flask app
# ======================
app = Flask(__name__)
CORS(app)

# Optional: limit upload size (500 MB)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

# ======================
# 2️⃣ Health check
# ======================
@app.route('/')
def index():
    return '✅ Video Converter Backend is running!'

# ======================
# 3️⃣ Video conversion
# ======================
@app.route('/convert', methods=['POST'])
def convert():
    uploaded_file = request.files.get('file')
    to_format = request.form.get('to_format', '').lower()

    if not uploaded_file or uploaded_file.filename == '':
        return jsonify({'error': 'No file uploaded'}), 400

    allowed_formats = ['mp4', 'mkv', 'webm']
    if to_format not in allowed_formats:
        return jsonify({'error': f'Unsupported format: {to_format}'}), 400

    with tempfile.TemporaryDirectory() as tmpdir:
        # Save uploaded file
        input_filename = secure_filename(uploaded_file.filename)
        input_path = os.path.join(tmpdir, input_filename)
        uploaded_file.save(input_path)

        # Prepare output path
        output_filename = f"output.{to_format}"
        output_path = os.path.join(tmpdir, output_filename)

        # FFmpeg command
        if to_format == 'webm':
            cmd = [
                'ffmpeg', '-i', input_path,
                '-c:v', 'libvpx-vp9',
                '-c:a', 'libopus',
                '-b:v', '1M',
                output_path
            ]
        else:
            cmd = [
                'ffmpeg', '-i', input_path,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-b:v', '1M',
                output_path
            ]

        # Run FFmpeg
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print(result.stderr.decode())
            return jsonify({'error': 'Conversion failed'}), 500

        return send_file(output_path, as_attachment=True)

# ======================
# 4️⃣ WSGI production: no app.run()
# ======================
# Do NOT include:
# if __name__ == '__main__':
#     app.run()
# Gunicorn will serve it: gunicorn -w 4 -b 0.0.0.0:5000 app:app
