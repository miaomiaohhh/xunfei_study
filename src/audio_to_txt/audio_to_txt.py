import os
from flask import jsonify
from Ifasr_app import audio2txt_Api, InputAns
import json5

UPLOAD_ANS = 'standardanswer'  # 上传作为答案的文件
UPLOAD_AUDIO = 'audio'
AUDIO2CONTEXT = 'res_context'
audio_folder = UPLOAD_AUDIO

with open('../../config.json', encoding='utf-8') as f:
    config = json5.load(f)
appid = config['appid']
api_secret = config['api_secret']
secret_key = config['secret_key']
api_key = config['api_key']


def run_the_assistant(inputans1,filename_list):
    # 检查文件夹是否为空
    if not os.listdir(audio_folder):
        # 如果为空，直接返回错误
        return jsonify({'error': '音频暂存区中没有文件，请上传音频文件后再试。'}), 400

    # 若文件夹不为空，则继续处理
    if not os.path.exists('res_context'):
        os.makedirs('res_context')
    if not os.path.exists('result'):
        os.makedirs('result')
    results = []  # 改动：用于存储多个文件的处理结果
    # 待比较的两个字符串变量
    #首先读取表达文件内容字符串'
    with open(inputans1, 'r', encoding='utf-8') as file:
        standardanswer_string = file.read()
    for eachname in os.listdir(audio_folder):  # 遍历所有需要检查的音频文件
        to_judge_file_path = os.path.join(audio_folder, eachname)
        # 为每个文件创建 RequestApi 实例
        api = audio2txt_Api(appid=appid, secret_key=secret_key, upload_file_path=to_judge_file_path, eachname=eachname)
        # 获取学生背诵结果字符串result
        result = api.get_result(op=1)
        os.remove(to_judge_file_path)  # 每次调用后删除上传的文件，避免服务器上文件堆积

        results.append(result)  # 改动：将每个文件的结果添加到结果列表中

    # 返回所有处理后的结果
    inputans = InputAns()
    inputans.ans_file_name = inputans1
    print("准备比较产生accuracy结果")
    print('standardanswer_string:',standardanswer_string)
    print('result: ',results)
    accuracy_response = inputans.compare_with_answer(standardanswer_string,results,filename_list)#result是所有上传音频的字符串列表
    print('accuracy_response:', accuracy_response)
    return accuracy_response


def run_the_assistant_send_context_to_starfire():
    """
    完成一个课堂内容生成的部分流程
    1.读取音频区（audio)的文件（这里必须规定只有一个文件）
    2.调用语音转写API
    3.得到音频文件的文字版放在res_context
    TODO: 星火大模型API部分需要拿走res_context中的文件再处理，
    在星火大模型部分调用这个方法。
    :return:
    """
    # 检查文件夹中文件数量
    audio_files = os.listdir(audio_folder)
    if len(audio_files) != 1:
        # 如果不止一个文件或无文件，直接返回错误
        return jsonify({'error': '音频暂存区内必须仅有一个文件。请确保上传了一个并且只有一个音频文件。'}), 400

    audio_file = audio_files[0]
    audio_file_path = os.path.join(audio_folder, audio_file)

    # 创建 RequestApi 实例
    api = audio2txt_Api(appid=appid, secret_key=secret_key, upload_file_path=audio_file_path)

    # 获取结果
    result = api.get_result(op=0)
    os.remove(audio_file_path)  # 删除上传的文件，避免服务器上文件堆积

    # 直接返回处理后的结果
    return jsonify(result), 200
