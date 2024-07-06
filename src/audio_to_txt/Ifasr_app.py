# -*- coding: utf-8 -*-
import Levenshtein
from flask import Flask, request, jsonify, render_template, redirect, url_for
import base64
import hashlib
import hmac
import json
import os
import time
import requests
import urllib
import random
import os
from src.spark.SparkApi import SparkLLM
import time
import json5


UPLOAD_ANS = 'uploads'  # 上传作为答案的文件
UPLOAD_AUDIO = 'audio'
AUDIO2CONTEXT = 'res_context'

UPLOAD_AUDIO = UPLOAD_AUDIO
AUDIO2CONTEXT = AUDIO2CONTEXT
audio_folder = UPLOAD_AUDIO

lfasr_host = 'https://raasr.xfyun.cn/v2/api'
# 请求的接口名
api_upload = '/upload'
api_get_result = '/getResult'



domain = "generalv3.5"    # v3.0版本
Spark_url = "wss://spark-api.xf-yun.com/v3.5/chat"  # v3.5环服务地址

with open('../../config.json', encoding='utf-8') as f:
    config = json5.load(f)
appid = config['appid']
api_secret = config['api_secret']
secret_key = config['secret_key']
api_key = config['api_key']

def extract_w_values(input_string):
    result = ''
    index = 0
    # 循环遍历字符串查找"w"属性
    while index < len(input_string):
        index = input_string.find('"w":"', index)
        if index == -1:  # 如果没有找到，结束循环
            break
        start = index + 5  # "w":"的结束位置即是我们需要的值的开始位置
        end = input_string.find('"', start)  # 查找值的结束位置
        result += input_string[start:end] + ' '  # 将找到的值加到结果字符串中
        index = end + 1
    return result.rstrip()  # 返回结果字符串，并移除末尾的空格


class audio2txt_Api(object):
    def __init__(self, appid, secret_key, upload_file_path, eachname):
        self.appid = appid
        self.secret_key = secret_key
        self.upload_file_path = upload_file_path
        self.eachname = eachname
        self.ts = str(int(time.time()))
        self.signa = self.get_signa()
        # 待比较的两个字符串变量
        self.standardanswer_string = ''
        self.studentanswer_string = ''

    def get_signa(self):
        appid = self.appid
        secret_key = self.secret_key
        m2 = hashlib.md5()
        m2.update((appid + self.ts).encode('utf-8'))
        md5 = m2.hexdigest()
        md5 = bytes(md5, encoding='utf-8')
        # 以secret_key为key, 上面的md5为msg， 使用hashlib.sha1加密结果为signa
        signa = hmac.new(secret_key.encode('utf-8'), md5, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, 'utf-8')
        return signa

    def upload(self):
        print("上传部分：")

        upload_file_path = self.upload_file_path
        file_len = os.path.getsize(upload_file_path)
        file_name = os.path.basename(upload_file_path)

        param_dict = {}
        param_dict['appId'] = self.appid
        param_dict['signa'] = self.signa
        param_dict['ts'] = self.ts
        param_dict["fileSize"] = file_len
        param_dict["fileName"] = file_name
        param_dict["duration"] = "200"
        print("upload参数：", param_dict)
        data = open(upload_file_path, 'rb').read(file_len)

        response = requests.post(url=lfasr_host + api_upload + "?" + urllib.parse.urlencode(param_dict),
                                 headers={"Content-type": "application/json"}, data=data)
        print("upload_url:", response.request.url)
        result = json.loads(response.text)
        print("upload resp:", result)
        return result

    def get_result(self, op):
        """
        op = 0时，使用星火大模型优化
        """
        uploadresp = self.upload()
        orderId = uploadresp['content']['orderId']
        param_dict = {}
        param_dict['appId'] = self.appid
        param_dict['signa'] = self.signa
        param_dict['ts'] = self.ts
        param_dict['orderId'] = orderId
        param_dict['resultType'] = "transfer,predict"
        print("")
        print("查询部分：")
        print("get result参数：", param_dict)
        status = 3
        # 建议使用回调的方式查询结果，查询接口有请求频率限制
        while status == 3:
            response = requests.post(url=lfasr_host + api_get_result + "?" + urllib.parse.urlencode(param_dict),
                                     headers={"Content-type": "application/json"})
            # print("get_result_url:",response.request.url)
            result = json.loads(response.text)
            print(result)
            status = result['content']['orderInfo']['status']
            context = result['content']['orderResult']  # 返回的文本结果
            context = context.replace("\\", "")

            print("status=", status)
            if status == 4:
                break
            time.sleep(5)
        print("get_result resp:", result)
        result_context = extract_w_values(context)
        result_context = result_context.replace(" ", "")

        print("res:", result_context)
        directory = AUDIO2CONTEXT
        if not os.path.exists(directory):
            os.makedirs(directory)

        # 为用户提供提示并获取输入的文件名
        file_name = self.eachname

        # 用.txt扩展名完善文件名
        file_name_with_extension = file_name + '.txt'

        if op == 0:
            llm = SparkLLM(appid, api_key, api_secret, Spark_url, domain)
            Input = "请提炼这段文字，只保留其中与课堂内容相关的部分:+" + result_context
            result_context = llm.query(Input)

        if op == 2:
            llm = SparkLLM(appid, api_key, api_secret, Spark_url, domain)
            Input = "请提炼这段文字，使其成为对某个问题的回答:+" + result_context
            result_context = llm.query(Input)

        # 保存字符串到指定文件
        string_to_save = result_context
        self.studentanswer_string = string_to_save
        print("音频解析结果：",string_to_save)
        # with open(os.path.join(directory, file_name_with_extension), 'w') as file:
        #     file.write(string_to_save)
        # print(f"文件已保存在 {directory}{file_name_with_extension}")
        return result_context


class InputAns(object):
    def __init__(self):
        self.result = "./result/result.json"

    def calculate_accuracy(self, standardanswer_string, studentanswer_string):
        print('Into calculate_accuracy')
        # with open(answer_file, 'r') as file:
        #     answer_content = file.read()
        # with open(compare_file, 'r') as file:
        #     compare_content = file.read()
        # print("待比较的两个文件读取成功")
        # distance = Levenshtein.distance(answer_content, compare_content)
        # similarity = 1 - distance / max(len(answer_content), len(compare_content))
        distance = Levenshtein.distance(standardanswer_string, studentanswer_string)
        similarity = 1 - distance / max(len(standardanswer_string), len(studentanswer_string))
        print("similarity:",similarity)
        return similarity

    def compare_with_answer(self, standard_answer, student_answers,filename_list):
        results = {}
        for i, student_answer in enumerate(student_answers):
            print("student_answer:",student_answer)
            accuracy = self.calculate_accuracy(standard_answer, student_answer)
            results[f'{filename_list[i]}'] = f"准确率: {accuracy:.2%}"
        # 将结果写入JSON文件
        with open(self.result, 'w', encoding='utf-8') as result_file:
            json.dump(results, result_file, ensure_ascii=False, indent=4)
        return results

    def compare_with_answer_nolongerused(self):
        if not self.ans_file_name:
            return "错误：没有指定答案文件。"

        results = {}
        with open(self.result, 'w') as result_file:
            # 遍历 res_context 目录下所有 txt 文件
            for filename in os.listdir(app.config('AUDIO2CONTEXT')):
                if filename.endswith('.txt'):
                    # 计算每个文件与答案的准确率
                    accuracy = self.calculate_accuracy(self.ans_file_name, os.path.join(AUDIO2CONTEXT,
                                                                                        filename))
                    filename_without_extension = os.path.splitext(filename)[0]
                    # 写入准确率到结果文件
                    results[filename_without_extension] = f"准确率: {accuracy}"
            json.dump(results, result_file, ensure_ascii=False, indent=4)
