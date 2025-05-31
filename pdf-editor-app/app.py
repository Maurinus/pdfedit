from flask import Flask, render_template, request, send_from_directory, jsonify
import os
from pdf2docx import Converter
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converted'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'pdf' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'})

    file = request.files['pdf']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'})

    if file and file.filename.endswith('.pdf'):
        unique_id = str(uuid.uuid4())
        pdf_path = os.path.join(UPLOAD_FOLDER, f'{unique_id}.pdf')
        docx_path = os.path.join(CONVERTED_FOLDER, f'{unique_id}.docx')

        file.save(pdf_path)

        try:
            cv = Converter(pdf_path)
            cv.convert(docx_path, start=0, end=None)
            cv.close()
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

        return jsonify({
            'success': True,
            'download_url': f'/download/{unique_id}.docx'
        })

    return jsonify({'success': False, 'error': 'Invalid file type'})

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(CONVERTED_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)