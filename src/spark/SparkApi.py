import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
import time
from urllib.parse import urlparse
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
import websocket  # 使用websocket_client
from ..utils import Logger

MAX_HISTORY_LEN = 8000

class SparkLLM(object):
    """_summary_
    用于与星火大模型对话
    """
    def __init__(self, appid, api_key, api_secret, Spark_url, domain, enable_history=True, history=[]):
        """
        Args:
            appid (str): 从控制台获取的APPID
            api_key (str): 从控制台获取的API_KEY
            api_secret (str): 从控制台获取的API_SECRET
            Spark_url (str): 星火大模型的url
            domain (str): 星火大模型的domain
            enable_history (bool): 是否启用历史记录
            history (list): 初始历史记录, 格式如下:
            [
                {"role": "system", "content": "你现在扮演李白，你豪情万丈，狂放不羁；接下来请用李白的口吻和用户对话。"} , # 设置对话背景或者模型角色
                {"role": "user", "content": "你是谁"},  # 用户的历史问题
                {"role": "assistant", "content": "....."} , # AI的历史回答结果
                ....... 省略的历史对话
                {"role": "user", "content": "你会做什么"}  # 最新的一条问题，如无需上下文，可只传最新一条问题
            ]
        """
        self.answer = ""
        self.sid = ''
        self.appid = appid
        self.api_key = api_key
        self.api_secret = api_secret
        self.Spark_url = Spark_url
        self.domain = domain
        self.history = history
        self.enable_history = enable_history
    
    def on_message(self, ws, message):
        """
        用于处理websocket收到的消息的回调函数
        """
        data = json.loads(message)
        code = data['header']['code']
        if code != 0:
            Logger.error(f'请求错误: {code}, {data}')
            ws.close()
        else:
            self.sid = data["header"]["sid"]
            choices = data["payload"]["choices"]
            status = choices["status"]
            content = choices["text"][0]["content"]
            Logger.info(content)
            self.answer += content
            if status == 2:
                ws.close()
    
    def query(self, question):
        """
        向星火大模型发送问题
        Args:
            question (str): 用户的问题

        Returns:
            str | False: 星火大模型的回答, 如果问题长度超过MAX_HISTORY_LEN则返回False
        """
        wsParam = Ws_Param(self.appid, self.api_key, self.api_secret, self.Spark_url)
        websocket.enableTrace(False)
        wsUrl = wsParam.create_url()
        ws = websocket.WebSocketApp(wsUrl, on_message=self.on_message, on_error=on_error, on_close=on_close, on_open=on_open)
        ws.appid = self.appid
        ws.domain = self.domain
        if(not self.enable_history):
            self.clearHistory()
        
        self.appendHistory("user", question)
        if(not self.checkHistoryLen()):
            return False
        ws.question = self.history
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        self.appendHistory("assistant", self.answer)
        tmp = self.answer
        self.answer = ""
        return tmp
    
    def clearHistory(self):
        """_summary_
        清空历史记录
        """
        self.history = []
        
    def setHistory(self, history):
        self.history = history
        
    def appendHistory(self, role,content):
        jsoncon = {}
        jsoncon["role"] = role
        jsoncon["content"] = content
        self.history.append(jsoncon)

    def checkHistoryLen(self):
        if(len(self.history[-1]['content']) > MAX_HISTORY_LEN):
            Logger.error("The length of the last content in history is greater than MAX_HISTORY_LEN")
            return False
        while (getHistoryLen(self.history) > MAX_HISTORY_LEN):
            del self.history[0]
        return True

# WebSocket参数类，用于生成合适的wsurl
class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, Spark_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(Spark_url).netloc
        self.path = urlparse(Spark_url).path
        self.Spark_url = Spark_url

    # 生成url
    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接鉴权参数，生成url
        url = self.Spark_url + '?' + urlencode(v)
        # print(url)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        return url

# 收到websocket错误的处理
def on_error(ws, error):
    Logger.error("SparkLLM error", error)
# 收到websocket关闭的处理
def on_close(ws,one,two):
    Logger.info("close websocket")
# 收到websocket连接建立的处理
def on_open(ws):
    thread.start_new_thread(run, (ws,))
def run(ws, *args):
    data = json.dumps(gen_params(appid=ws.appid, domain= ws.domain,question=ws.question))
    ws.send(data)
def gen_params(appid, domain,question):
    """
    通过appid和用户的提问来生成请参数
    """
    data = {
        "header": {
            "app_id": appid,
            "uid": "1234"
        },
        "parameter": {

            "chat": {
                "domain": domain,
                "temperature": 0.8,
                "max_tokens": 2048,
                "top_k": 5,

                "auditing": "default"
            }
        },
        "payload": {
            "message": {
                "text": question
            }
        }
    }
    return data
def getHistoryLen(text):
    length = 0
    for content in text:
        temp = content["content"]
        leng = len(temp)
        length += leng
    return length


