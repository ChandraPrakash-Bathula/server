from flask import Flask, request, send_file
import os
import subprocess
import tempfile
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/convert', methods=['POST'])
def convert():
    uploaded_file = request.files['file']
    to_format = request.form['to_format'].lower()

    if uploaded_file.filename == '':
        return 'No file uploaded', 400

    allowed_formats = ['mp4', 'mkv', 'mov', 'avi', 'flv', 'wmv', 'm4v', '3gp', 'ogv', 'webm']
    if to_format not in allowed_formats:
        return f'Unsupported target format: {to_format}', 400

    with tempfile.TemporaryDirectory() as tmpdir:
        input_filename = secure_filename(uploaded_file.filename)
        input_path = os.path.join(tmpdir, input_filename)
        uploaded_file.save(input_path)

        name_wo_ext = os.path.splitext(input_filename)[0]
        from_ext = os.path.splitext(input_filename)[1][1:].lower()
        output_filename = f"{name_wo_ext}.{to_format}"
        output_path = os.path.join(tmpdir, output_filename)

        # ✅ Default codecs
        video_codec = 'libx264'
        audio_codec = 'aac'

        # ✅ Special case for webm
        if to_format == 'webm':
            video_codec = 'libvpx-vp9'
            audio_codec = 'libopus'

        # ✅ Decide if remux is possible (same codec container swap)
        # E.g., mkv (H.264) → mp4 (H.264) → remux
        remux_possible = False
        if from_ext in ['mkv', 'mov'] and to_format == 'mp4':
            remux_possible = True
        elif from_ext == 'mp4' and to_format in ['mkv', 'mov']:
            remux_possible = True

        # ✅ Build ffmpeg command
        if remux_possible:
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-c', 'copy',
                output_path
            ]
            print("⚡ Using remux for fast container swap!")
        else:
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-c:v', video_codec,
                '-c:a', audio_codec,
                '-strict', 'experimental',
                output_path
            ]
            print(f"🔥 Doing full re-encode: {video_codec} + {audio_codec}")

        # ✅ Run ffmpeg
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print(result.stderr.decode())
            return 'Conversion failed', 500

        return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
