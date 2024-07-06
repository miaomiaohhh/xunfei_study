from flask_cors import CORS
import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from docx import Document
from official_doc_check import official_doc_check

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = 'uploads'

ALLOWED_EXTENSIONS = {'txt', 'doc', 'docx'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def text_from_docx(file_path):
    doc = Document(file_path)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return '\n'.join(fullText)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # 根据文件类型选择处理方式
        if filename.endswith('.txt'):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        elif filename.endswith(('.doc', '.docx')):
            content = text_from_docx(filepath)
        else:
            return 'File format not supported', 400

        # 调用fun函数处理content
        processed_content = official_doc_check(content)

        # 将处理结果保存到txt文件
        result_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'result.txt')
        with open(result_filepath, 'w', encoding='utf-8') as f:
            f.write(processed_content)

        # 返回结果文件给前端
        return jsonify({'message': 'File processed successfully', 'filename': 'result.txt'}), 200
    else:
        return 'No file uploaded or file type not allowed', 400


if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    app.run(host='0.0.0.0', port=5000)