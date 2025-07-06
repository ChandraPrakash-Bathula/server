import os
from flask import Flask, request, send_file
from flask_cors import CORS
import tempfile
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # Limit to 500 MB

@app.route('/')
def index():
    return '✅ Video Converter Backend is running!'

@app.route('/convert', methods=['POST'])
def convert():
    uploaded_file = request.files['file']
    to_format = request.form['to_format'].lower()

    if uploaded_file.filename == '':
        return 'No file uploaded', 400

    allowed_formats = ['mp4', 'mkv', 'webm']
    if to_format not in allowed_formats:
        return f'Unsupported format: {to_format}', 400

    with tempfile.TemporaryDirectory() as tmpdir:
        input_filename = secure_filename(uploaded_file.filename)
        input_path = os.path.join(tmpdir, input_filename)
        uploaded_file.save(input_path)

        output_filename = f"output.{to_format}"
        output_path = os.path.join(tmpdir, output_filename)

        cmd = ['ffmpeg', '-i', input_path, '-c:v', 'libx264', '-c:a', 'aac', output_path]
        if to_format == 'webm':
            cmd = ['ffmpeg', '-i', input_path, '-c:v', 'libvpx-vp9', '-c:a', 'libopus', output_path]

        subprocess.run(cmd)

        return send_file(output_path, as_attachment=True)

# Do not run with app.run() in production
