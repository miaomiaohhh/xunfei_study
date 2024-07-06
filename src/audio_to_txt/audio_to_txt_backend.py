from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import shutil
from werkzeug.utils import secure_filename
import time

from src.audio_to_txt.audio_to_txt import run_the_assistant

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'standardanswer'
AUDIO_FOLDER = 'audio'
STANDARD_ANSWER_FOLDER = 'standardanswer'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['AUDIO_FOLDER'] = AUDIO_FOLDER
app.config['STANDARD_ANSWER_FOLDER'] = STANDARD_ANSWER_FOLDER

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'pcm', 'aac', 'opus', 'flac', 'ogg', 'm4a', 'amr', 'speex', 'lyb', 'ac3', 'aac',
                      'ape', 'm4r', 'mp4', 'acc', 'wma','txt'}

timeout = 120 # 用于指定传送音频文件的时间上限

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/uploadhomework', methods=['POST'])
def upload_file():
    print("Into upload_file")
    num_files_expected = int(request.form['num_files'])  #TODO 前端需要传一个INT类型数字表示 待传输音频个数
    print('num_files_expected:',num_files_expected)
    # 运行前清空AUDIO_FOLDER
    if os.path.exists(app.config['AUDIO_FOLDER']):
        shutil.rmtree(app.config['AUDIO_FOLDER'])
    os.makedirs(app.config['AUDIO_FOLDER'])

    # 检查并保存标准答案文件
    if 'answer' not in request.files:
        return 'No answer file part', 400
    answer_file = request.files['answer']
    if answer_file.filename == '':
        return 'No selected answer file', 400
    if not allowed_file(answer_file.filename):
        return 'File type not allowed', 400
    answer_filename = secure_filename(answer_file.filename)
    print(answer_filename)
    if not os.path.exists(app.config['STANDARD_ANSWER_FOLDER']):
        os.makedirs(app.config['STANDARD_ANSWER_FOLDER'])
    answer_path = os.path.join(app.config['STANDARD_ANSWER_FOLDER'], answer_filename)
    answer_file.save(answer_path)

    # 由于文件上传有延时，这里我们用一个简单的轮询方法检查文件是否全部到达
    start_time = time.time()
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time > timeout:
            return 'File upload timed out', 408

        audio_files = request.files.getlist('audio_files')   #TODO 前端传输的音频
        if len(audio_files) == num_files_expected:
            break
        time.sleep(1)
    filename_list = []
    for file in audio_files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(file.filename)
            filename_list.append(file.filename)
            file.save(os.path.join(app.config['AUDIO_FOLDER'], filename))
    if not audio_files:
        return 'No audio files uploaded', 400
    # print('inputans1: ',os.path.join(app.config['UPLOAD_FOLDER'], 'standardanswer.txt'))
    accuracy_results = run_the_assistant(inputans1=os.path.join(app.config['UPLOAD_FOLDER'], 'standardanswer.txt'),filename_list=filename_list)
    print('Done run_the_assistant')
    return jsonify(accuracy_results)
    # result_json_path = os.path.join('res_context', 'result.json')
    # if os.path.exists(result_json_path):
    #     with open(result_json_path, 'r', encoding='utf-8') as file:
    #         result_data = file.read()
    #         return jsonify(result_data)
    # else:
    #     return 'Result JSON file does not exist', 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
