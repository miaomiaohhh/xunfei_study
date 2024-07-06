import re

from ..spark.SparkApi import SparkLLM
from ..audio_to_txt.Ifasr_app import audio2txt_Api

import random
from threading import Timer
import json5
import os
import sounddevice as sd
import numpy as np
import threading
import time
from pathlib import Path

with open('../config.json', encoding='utf-8') as f:
    config = json5.load(f)
appid = config['appid']
api_secret = config['api_secret']
api_key = config['api_key']
secret_key = config['secret_key']
audio_folder = "audio_to_txt/audio"
audio_tmp_folder = "audio_to_txt/tmp_audio"
context_folder = "./context"

domain = "generalv3.5"  # v3.0版本
Spark_url = "wss://spark-api.xf-yun.com/v3.5/chat"  # v3.5环服务地址


def select_from_database(name):
    pass


def save_to_database(name, data):
    pass  # 添加具体的数据库保存


# 全局变量，用于控制录音状态
qa_recording = True
is_recording = True
pause_recording = False


# 假设的录音函数,需要返回保存的文件路径
def record_audio(filename='tmp_question.wav', sample_rate=44100, channels=2):
    """
    开始录音，并在接收到停止指令时结束录音。

    参数:
    filename : str, optional
        存储录音的文件名（默认为output.wav）。
    sample_rate : int, optional
        每秒采样率（默认44100）。
    channels : int, optional
        录音通道数（默认2，即立体声）。
    """
    global qa_recording
    qa_recording = True

    global pause_recording
    pause_recording = True

    def recording_thread():
        global qa_recording
        print("开始录音…")
        # 使用sounddevice的InputStream实现实时录音
        with sd.InputStream(samplerate=sample_rate, channels=channels) as stream:
            audio_frames = []
            while qa_recording:
                frame, overflowed = stream.read(sample_rate)  # 每次读1秒的音频帧
                if overflowed:
                    print("警告: 音频缓冲区溢出")
                audio_frames.append(frame)
            # 归一化并保存音频文件
            # audio_dir_path = Path(__file__).parent.parent / 'audio_to_txt/audio'
            audio_dir_path = audio_tmp_folder
            os.makedirs(audio_dir_path, exist_ok=True)
            audio_file_path = audio_dir_path / filename
            audio_data = np.concatenate(audio_frames, axis=0).tobytes()
            with open(audio_file_path, 'wb') as audio_file:
                audio_file.write(audio_data)
            print(f"录音已停止，保存在：{audio_dir_path}/{filename}")

    # 创建录音线程
    thread = threading.Thread(target=recording_thread)
    thread.start()

    # 在主线程中等待用户输入停止指令
    while True:
        command = input()
        if command.lower() == 'stop':
            qa_recording = False
            break

    # 等待录音线程结束
    thread.join()
    pause_recording = False  # 可以结束对课堂录音的暂停


def record_audio_for_whole_class(filename='output.wav', sample_rate=44100, channels=2):
    """
    开始录音，并在接收到暂停/恢复指令时控制录音的暂停与恢复。

    参数:
    filename : str, optional
        存储录音的文件名（默认为output.wav）。
    sample_rate : int, optional
        每秒采样率（默认44100）。
    channels : int, optional
        录音通道数（默认2，即立体声）。
    """
    global is_recording, pause_recording

    def recording_thread():
        global is_recording, pause_recording
        print("开始录音…")
        # 使用sounddevice的InputStream实现实时录音
        with sd.InputStream(samplerate=sample_rate, channels=channels) as stream:
            audio_frames = []
            while is_recording:
                if pause_recording:
                    continue
                frame, overflowed = stream.read(sample_rate)  # 每次读1秒的音频帧
                if overflowed:
                    print("警告: 音频缓冲区溢出")
                audio_frames.append(frame)
            # 归一化并保存音频文件
            # audio_dir_path = Path(__file__).parent.parent / 'audio_to_txt/audio'
            audio_dir_path = audio_folder
            os.makedirs(audio_dir_path, exist_ok=True)
            audio_file_path = audio_dir_path / filename
            audio_data = np.concatenate(audio_frames, axis=0).tobytes()
            with open(audio_file_path, 'wb') as audio_file:
                audio_file.write(audio_data)
            print(f"录音已停止，保存在：{audio_dir_path}/{filename}")

    # 创建录音线程
    thread = threading.Thread(target=recording_thread)
    thread.start()

    # 在主线程中等待用户输入暂停/恢复/停止指令
    # 强制性的指令
    while True:
        command = input()
        if command.lower() == 'pause':
            pause_recording = True
            print('录音已暂停，等待恢复…')
        elif command.lower() == 'resume':
            pause_recording = False
            print('录音已恢复。')
        elif command.lower() == 'stop':
            is_recording = False
            break

    # 等待录音线程结束
    thread.join()


def random_call_and_record(class_name, course_name):
    students = []  # 这里需要写一个从数据库中选择数据的函数
    selected_student = random.choice(students)
    print(f"点到的学生是：{selected_student}")
    record_audio()  # 开始录音
    valid = input("是否是有效回答？")
    if valid:
        score = input(f"给{selected_student}的回答输入一个0-5的分数: ")
        save_to_database('class_records',
                         {'class_name': class_name, 'student': selected_student, 'course_name': course_name,
                          'score': score})


def start_class():
    if_record = 0
    course_name = input("请输入本节课程名: ")
    class_name = input("请输入班级名: ")  # 从数据库中选择班级
    end_time = input("请输入下课时间（例如15:30）: ")
    if_record = input("是否开始录音")

    if if_record:
        filename = input()  # 前端给出，前端默认值为课堂名
        record_audio_for_whole_class(filename=filename)

    # 这里设置一个倒计时，到点结束课堂
    countdown_timer = Timer(60 * 60, end_class)  # 具体时间需要根据end_time计算
    countdown_timer.start()  # 启动倒计时

    while 1:
        command = input("等待指令（1-随机点名；2-AI回答；3-结束课堂, 4-课堂测试, 5-开启录音): ")  # TODO 前端点击选择
        if command == "1":
            random_call_and_record(class_name, course_name)
        elif command == "2":
            audio = record_audio()  # 针对问题开始录音
            print("录音已经保存到临时文件夹。")
            llm = SparkLLM(appid, api_key, api_secret, Spark_url, domain)
            audio2txt = audio2txt_Api(appid, secret_key, os.path.join(audio_tmp_folder, "tmp_question.wav"), "bot_ans")
            # 这里会保存在 audio_to_text/res_context目录下
            question = audio2txt.get_result(op=2)
            ans = llm.query(question)
            print(ans)  # TODO 这个答案需要显示在前端
        elif command == "3":
            break
        elif command == "4":
            # AI课堂小测？ 可以结合 1 出题
            pass
        elif command == "5":  # 开启录音
            global is_recording
            if is_recording:
                check = input("你有正在进行的录音，是否结束")
                if check:
                    is_recording = 0
                    time.sleep(1)
                else:
                    continue
            else:
                time.sleep(1)
            if_record = 1
            filename = input()  # 前端给出，前端默认值为课堂名
            record_audio_for_whole_class(filename=filename)

    if if_record:  # 只要在本堂课内至少启动一次录音就可以
        if_save_content = input("是否保留这堂课的内容？")
        if if_save_content:
            cnt = 1
            for foldername, filenames in os.walk(audio_folder):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    audio2txt = audio2txt_Api(appid, secret_key, file_path, f"whole_class_part{cnt}")
                    cnt += 1

            # 定位到目标文件夹
            audio_dir = '../audio_to_txt/res_context'

            # 获取所有符合条件的文件名，并根据文件名中的数字排序
            file_list = [
                f for f in os.listdir(audio_dir)
                if re.match(r'whole_class_part(\d+)\.txt', f)
            ]
            file_list.sort(key=lambda x: int(re.findall(r'(\d+)', x)[0]))  # 根据数字进行排序

            # 读取文件内容并拼接
            whole_class_content = ''
            for file_name in file_list:
                part_number = re.findall(r'(\d+)', file_name)[0]
                with open(os.path.join(audio_dir, file_name), 'r') as file:
                    content = file.read()
                    whole_class_content += f"第{part_number}部分：\n{content}\n"

                # 删除原文件
                os.remove(os.path.join(audio_dir, file_name))

            # 写入新文件
            with open('../audio_to_txt/whole_class.txt', 'w') as file:
                file.write(whole_class_content)  # TODO: 这里应该永久地保存到数据库

            print(whole_class_content)

    end_class()


def end_class():
    # 这里处理课堂结束的逻辑，比如关闭倒计时，保存课堂记录等
    print("课堂已经结束。")


if __name__ == '__main__':
    start_class()
