# 基于星火大模型的智能课程推荐
from src.spark.SparkApi import SparkLLM
import time
import json5
from reptile.from_coursera import reptile_from_coursera
from reptile.from_edx import reptile_from_edx

with open('../config.json', encoding='utf-8') as f:
    config = json5.load(f)
appid = config['appid']
api_secret = config['api_secret']
api_key = config['api_key']

domain = "generalv3.5"  # v3.0版本
Spark_url = "wss://spark-api.xf-yun.com/v3.5/chat"  # v3.5环服务地址


def search_ans_in_database(num: int):
    """
    从数据库中根据课程编号搜索课程
    return:课程的url，与简介，最好能带一张图片
    """
    pass


def ai_recommend(Input: str):
    """
    param:
    Input:接收从前端的课程需求
    """
    reptile_from_coursera()
    reptile_from_edx()
    llm = SparkLLM(appid, api_key, api_secret, Spark_url, domain)
    class_list = []  # 从数据库中读取课程文件和课程介绍
    class_list_str = ""
    cnt = 0
    for each_class in class_list:
        cnt += 1
        class_list_str += (str(cnt) + ":" + each_class + "\t")

    ans = llm.query(
        Input + "请从下列课程中选择出最符合我要求的课程，（给出课程编号，要求你只回答一个数字）：" + class_list_str)

    ans = int(ans)
    res = search_ans_in_database(ans)
    return res
