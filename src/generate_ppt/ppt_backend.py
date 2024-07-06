from flask_cors import CORS
import requests
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import os
from run_generate_app import generate_ppt

# 创建服务器
app = Flask(__name__)
CORS(app)

# 定义文件上传的目录
UPLOAD_FOLDER = 'pre_text'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# 定义路由，用于文件上传
@app.route('/uploadppt', methods=['POST', 'GET'])
def upload_file():
    # 检查是否有文件在请求内
    if 'file' not in request.files:
        return 'No file part in the request'
    file = request.files['file']
    theme = request.form['theme']
    is_card_note = request.form['is_card_note']
    is_card_note = int(is_card_note)

    # 如果用户没有选择文件，浏览器也会提交一个空的文件无文件名
    if file.filename == '':
        return 'No selected file'

    if file:
        # 安全地获取文件名，并保存到服务器的 UPLOAD_FOLDER 目录下
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print(filename,theme,is_card_note,type(is_card_note))
        generate_ppt(filename, theme, is_card_note)
        return 'File successfully uploaded'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)