# -*- coding:utf-8 -*-
from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
import hashlib
import base64
import hmac
from urllib.parse import urlencode
import json
import requests

# 控制台获取
APPId = "e76d7d8f"
APISecret = "Y2Y2ODc2OGQyOWFjMWZhY2JkOTllMDVl"
APIKey = "990e2770b030441fbcc126c691daf5cd"


class AssembleHeaderException(Exception):
    def __init__(self, msg):
        self.message = msg


class Url:
    def __init__(this, host, path, schema):
        this.host = host
        this.path = path
        this.schema = schema
        pass


class WebsocketDemo:
    def __init__(self, APPId, APISecret, APIKey, Text):
        self.appid = APPId
        self.apisecret = APISecret
        self.apikey = APIKey
        self.text = Text
        self.url = 'https://cn-huadong-1.xf-yun.com/v1/private/s37b42a45'

    # calculate sha256 and encode to base64
    def sha256base64(self, data):
        sha256 = hashlib.sha256()
        sha256.update(data)
        digest = base64.b64encode(sha256.digest()).decode(encoding='utf-8')
        return digest

    def parse_url(self, requset_url):
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
    def assemble_ws_auth_url(self, requset_url, method="POST", api_key="", api_secret=""):
        u = self.parse_url(requset_url)
        host = u.host
        path = u.path
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        # print(date)
        # date = "Thu, 12 Dec 2019 01:57:27 GMT"
        signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(host, date, method, path)
        # print(signature_origin)
        signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            api_key, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # print(authorization_origin)
        values = {
            "host": host,
            "date": date,
            "authorization": authorization
        }

        return requset_url + "?" + urlencode(values)

    def get_body(self):
        body = {
            "header": {
                "app_id": self.appid,
                "status": 3,
                # "uid":"your_uid"
            },
            "parameter": {
                "midu_correct": {
                    # "res_id":"your_res_id",
                    "output_result": {
                        "encoding": "utf8",
                        "compress": "raw",
                        "format": "json"
                    }
                }
            },
            "payload": {
                "text": {
                    "encoding": "utf8",
                    "compress": "raw",
                    "format": "plain",
                    "status": 3,
                    "text": base64.b64encode(self.text.encode("utf-8")).decode('utf-8')
                }
            }
        }
        return body

    def get_result(self):
        request_url = self.assemble_ws_auth_url(self.url, "POST", self.apikey, self.apisecret)
        headers = {'content-type': "application/json", 'host': 'api.xf-yun.com', 'app_id': self.appid}
        body = self.get_body()
        response = requests.post(request_url, data=json.dumps(body), headers=headers)
        print('onMessage：\n' + response.content.decode())
        tempResult = json.loads(response.content.decode())
        print('公文校对text字段解析：\n' + base64.b64decode(tempResult['payload']['output_result']['text']).decode())
        return base64.b64decode(tempResult['payload']['output_result']['text']).decode()


def replace_words(text, mode):
    # 读取mode字符串为JSON对象
    mode_json = json.loads(mode)

    # 检查数据字典中的'checklist'是否存在
    if 'checklist' in mode_json['data']:
        # 逆序遍历错误列表，这样我们不会因修改文本而影响后续替换的位置
        for error in reversed(mode_json['data']['checklist']):
            # 获取错误单词的位置和长度
            position = error['position']
            length = error['length']

            # 将suggest数组转换成字符串，这里假设suggest数组中总是有一个建议
            suggestion = error['suggest'][0] if error['suggest'] else ''

            # 根据位置和长度替换掉错误的单词
            text = text[:position] + suggestion + text[position + length:]

    return text


def official_doc_check(Text: str):
    demo = WebsocketDemo(APPId, APISecret, APIKey, Text)
    result = demo.get_result()  # 这里返回了一个string类型的响应
    Modified_Text = replace_words(Text, result)
    print(Modified_Text)
