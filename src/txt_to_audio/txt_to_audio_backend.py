from flask_cors import CORS
import requests
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import os
from text_speech_synthesis import txt_to_audio

# 创建服务器
app = Flask(__name__)
CORS(app)

# 定义文件上传的目录
UPLOAD_FOLDER = 'context'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# 定义路由，用于文件上传
@app.route('/upload', methods=['POST', 'GET'])
def upload_file():
    # 检查是否有文件在请求内
    if 'file' not in request.files:
        return 'No file part in the request'

    file = request.files['file']
    speed = request.files['speed']
    volumn = request.files['volumn']
    language = request.files['language']

    # 如果用户没有选择文件，浏览器也会提交一个空的文件无文件名
    if file.filename == '':
        return 'No selected file'

    if file:
        # 安全地获取文件名，并保存到服务器的 UPLOAD_FOLDER 目录下
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        txt_to_audio(file, speed, volumn, language)
        return 'File successfully uploaded'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
