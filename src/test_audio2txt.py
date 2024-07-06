from audio_to_txt.Ifasr_app import audio2txt_Api
import time
import json5
import os

with open('../config.json', encoding='utf-8') as f:
    config = json5.load(f)
appid = config['appid']
api_secret = config['api_secret']
api_key = config['api_key']
secret_key = config['secret_key']
audio_folder = "audio_to_txt/audio"

domain = "generalv3.5"    # v3.0版本
Spark_url = "wss://spark-api.xf-yun.com/v3.5/chat"  # v3.5环服务地址

if __name__ == '__main__':
    for eachname in os.listdir(audio_folder):  # 遍历所有需要检查的音频文件
        to_judge_file_path = os.path.join(audio_folder, eachname)
        # 为每个文件创建 RequestApi 实例
        api = audio2txt_Api(appid=appid, secret_key=secret_key, upload_file_path=to_judge_file_path, eachname=eachname)
        api.get_result(op=1)  # TODO 这里文件保存的路径稍微有点问题