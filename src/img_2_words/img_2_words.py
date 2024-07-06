import os
from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
import hashlib
import base64
import hmac
from urllib.parse import urlencode
import json
import requests

'''
1、通用文字识别,图像数据base64编码后大小不得超过10M
2、appid、apiSecret、apiKey请到讯飞开放平台控制台获取并填写到此demo中
3、支持中英文,支持手写和印刷文字。
4、在倾斜文字上效果有提升，同时支持部分生僻字的识别
'''

APPId = "e76d7d8f"  # 控制台获取

APISecret = "Y2Y2ODc2OGQyOWFjMWZhY2JkOTllMDVl"  # 控制台获取
APIKey = "990e2770b030441fbcc126c691daf5cd"  # 控制台获取


class AssembleHeaderException(Exception):
    def __init__(self, msg):
        self.message = msg


class Url:
    def __init__(self, host, path, schema):
        self.host = host
        self.path = path
        self.schema = schema
        pass


# calculate sha256 and encode to base64
def sha256base64(data):
    sha256 = hashlib.sha256()
    sha256.update(data)
    digest = base64.b64encode(sha256.digest()).decode(encoding='utf-8')
    return digest


def parse_url(requset_url):
    stidx = requset_url.index("://")
    host = requset_url[stidx + 3:]
    schema = requset_url[:stidx + 3]
    edidx = host.index("/")
    if edidx <= 0:
        raise AssembleHeaderException("invalid request url:" + requset_url)
    path = host[edidx:]
    host = host[:edidx]
    u = Url(host, path, schema)
    return u


# build websocket auth request url
def assemble_ws_auth_url(requset_url, method="POST", api_key="", api_secret=""):
    u = parse_url(requset_url)
    host = u.host
    path = u.path
    now = datetime.now()
    date = format_date_time(mktime(now.timetuple()))
    print(date)
    # date = "Thu, 12 Dec 2019 01:57:27 GMT"
    signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(host, date, method, path)
    print(signature_origin)
    signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                             digestmod=hashlib.sha256).digest()
    signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
    authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
        api_key, "hmac-sha256", "host date request-line", signature_sha)
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
    print(authorization_origin)
    values = {
        "host": host,
        "date": date,
        "authorization": authorization
    }

    return requset_url + "?" + urlencode(values)


class img_2_words:
    def __init__(self, appid, APIKey, APISecret):
        self.way = "POST"
        self.appid = appid
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.url = 'https://api.xf-yun.com/v1/private/sf8e6aca1'

    def run(self):
        image_folder_path = 'image'
        imageBytes = b''
        for filename in os.listdir(image_folder_path):
            # 构建文件的完整路径
            file_path = os.path.join(image_folder_path, filename)
            if os.path.isfile(file_path):
                # 检查文件扩展名
                if file_path.lower().endswith('.jpg') | file_path.lower().endswith('.jpeg') | \
                        file_path.lower().endswith('.png') | file_path.lower().endswith('.bmp'):
                    with open(file_path, "rb") as f:
                        imageBytes += f.read()  # 读取内容并拼接
                else:
                    raise ValueError("目前不支持该格式的文件: {}".format(file_path))

        body = {
            "header": {
                "app_id": APPId,
                "status": 3
            },
            "parameter": {
                "sf8e6aca1": {
                    "category": "ch_en_public_cloud",
                    "result": {
                        "encoding": "utf8",
                        "compress": "raw",
                        "format": "json"
                    }
                }
            },
            "payload": {
                "sf8e6aca1_data_1": {
                    "encoding": "jpg",
                    "image": str(base64.b64encode(imageBytes), 'UTF-8'),
                    "status": 3
                }
            }
        }

        request_url = assemble_ws_auth_url(self.url, "POST", APIKey, APISecret)
        headers = {'content-type': "application/json", 'host': 'api.xf-yun.com', 'app_id': APPId}
        print(request_url)
        response = requests.post(request_url, data=json.dumps(body), headers=headers)
        print(response)
        print(response.content)

        print("resp=>" + response.content.decode())
        tempResult = json.loads(response.content.decode())

        finalResult = base64.b64decode(tempResult['payload']['result']['text']).decode()
        finalResult = finalResult.replace(" ", "").replace("\n", "").replace("\t", "").strip()
        # 以JSON格式写入文件

        data_to_save = finalResult
        data = json.loads(data_to_save)

        words_content = []

        for page in data['pages']:
            for line in page['lines']:
                if 'words' in line:
                    for word in line['words']:
                        words_content.append(word['content'])

        result_string = ' '.join(words_content)

        with open('result/result.txt', 'w', encoding='utf-8') as f:
            f.write(result_string)

        print("内容已保存。")
        print(result_string)


def img_2_words_run():
    IMG2WORDS = img_2_words(APPId, APIKey, APISecret)
    IMG2WORDS.run()
