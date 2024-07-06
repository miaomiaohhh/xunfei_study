# -*- coding:utf-8 -*-
import hashlib
import hmac
import base64
import json
import os
import time
import requests
from pptx import Presentation
from PIL import Image
import matplotlib.pyplot as plt

class AIPPT():

    def __init__(self, APPId, APISecret, Text):
        self.APPid = APPId
        self.APISecret = APISecret
        self.text = Text
        self.header = {}

    # 获取签名
    def get_signature(self, ts):
        try:
            # 对app_id和时间戳进行MD5加密
            auth = self.md5(self.APPid + str(ts))
            # 使用HMAC-SHA1算法对加密后的字符串进行加密
            return self.hmac_sha1_encrypt(auth, self.APISecret)
        except Exception as e:
            print(e)
            return None

    def hmac_sha1_encrypt(self, encrypt_text, encrypt_key):
        # 使用HMAC-SHA1算法对文本进行加密，并将结果转换为Base64编码
        return base64.b64encode(
            hmac.new(encrypt_key.encode('utf-8'), encrypt_text.encode('utf-8'), hashlib.sha1).digest()).decode('utf-8')

    def md5(self, text):
        # 对文本进行MD5加密，并返回加密后的十六进制字符串
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    # 创建PPT生成任务
    def create_task(self,theme,is_card_note):
        url = 'https://zwapi.xfyun.cn/api/aippt/create'
        timestamp = int(time.time())
        signature = self.get_signature(timestamp)
        body = self.getbody(self.text, theme, is_card_note)

        headers = {
            "appId": self.APPid,
            "timestamp": str(timestamp),
            "signature": signature,
            "Content-Type": "application/json; charset=utf-8"
        }
        self.header = headers
        response = requests.request("POST", url=url, data=json.dumps(body), headers=headers).text
        resp = json.loads(response)
        if (0 == resp['code']):
            return resp['data']['sid']
        else:
            print('创建PPT任务成功')
            return None

    # 构建请求body体
    def getbody(self, text, theme, is_card_note):
        body = {
            "query": text,
            "theme": theme,
            "is_card_note": is_card_note
        }
        return body

    # 轮询任务进度，返回完整响应信息
    def get_process(self, sid):
        print("sid:" + sid)
        if (None != sid):
            response = requests.request("GET", url=f"https://zwapi.xfyun.cn/api/aippt/progress?sid={sid}",
                                        headers=self.header).text
            print(response)
            return response
        else:
            return None

    # 读取用户选择的文件并连接文本
    def get_text_content(self, user_text, selected_file_path):
        try:
            with open(selected_file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
            complete_text = user_text + ':' + file_content
            if len(complete_text) >= 8000:
                return None
            else:
                return complete_text
        except Exception as e:
            print(e)
            return None


    def get_result(self, theme='auto', is_card_note=0, selected_file_name=''):
        # 基于用户输入和文件内容组合文本
        self.text = self.get_text_content(self.text, os.path.join('pre_text', selected_file_name))
        print(self.text)
        if self.text is None:
            print("Error: The combined text length exceeds 8000 characters.")
            return None

        # 创建 PPT 生成任务
        print('theme,iscardnode',theme,is_card_note,type(is_card_note))
        task_id = self.create_task(theme=theme, is_card_note=int(is_card_note))
        print('task_id:',task_id,type(task_id))
        # 轮询任务进度
        while True:
            response = self.get_process(task_id)
            resp = json.loads(response)
            process = resp['data']['process']
            if process == 100:
                PPTurl = resp['data']['pptUrl']
                self.download_file(PPTurl, selected_file_name)
                break

    def show_first_slide(self, ppt_file_path, scale_factor=0.01):
        try:
            prs = Presentation(ppt_file_path)
            slide = prs.slides[0]

            # 原始幻灯片尺寸
            slide_width = prs.slide_width
            slide_height = prs.slide_height
            print(f"原始幻灯片尺寸：{slide_width} x {slide_height}")

            # 计算缩放后的图像尺寸
            img_width = int(slide_width * scale_factor)
            img_height = int(slide_height * scale_factor)
            print(f"缩放后的图像尺寸：{img_width} x {img_height}")

            # 创建一个RGB模式的空白图像
            img = Image.new('RGB', (img_width, img_height), color='white')

            # 示例：将幻灯片内容绘制到图像上
            # （在这里添加绘制幻灯片内容的逻辑）

            # 显示图像
            plt.imshow(img)
            plt.axis('off')  # 不显示坐标轴
            plt.show()

        except MemoryError as e:
            print(f"内存错误：{e}")
            # 可以添加额外的处理逻辑，例如缩小缩放比例再尝试一次，或者处理分块保存等方法

        except Exception as e:
            print(f"显示幻灯片时出错：{e}")

            # 打印详细的异常信息以便调试
            import traceback
            traceback.print_exc()

    def download_file(self, url, file_name):
        response = requests.get(url)
        if response.status_code == 200:
            output_folder = 'generate_ppt'
            # 确保输出文件夹存在
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            # 修改后缀名为ppt
            file_name1, _ = os.path.splitext(file_name)
            ppt_file_name = file_name1 + '.ppt'
            file_path = os.path.join(output_folder, ppt_file_name)

            with open(file_path, 'wb') as file:
                file.write(response.content)
            print(f"File downloaded successfully: {file_path}")

            # 显示PPT的第一页
            self.show_first_slide(file_path)

        else:
            print("Failed to download file.")
