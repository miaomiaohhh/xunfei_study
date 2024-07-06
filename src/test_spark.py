from spark.SparkApi import SparkLLM
import time
import json5

with open('../config.json', encoding='utf-8') as f:
    config = json5.load(f)
appid = config['appid']
api_secret = config['api_secret']
api_key = config['api_key']

domain = "generalv3.5"    # v3.0版本
Spark_url = "wss://spark-api.xf-yun.com/v3.5/chat"  # v3.5环服务地址

if __name__ == '__main__':
    llm = SparkLLM(appid, api_key, api_secret, Spark_url, domain)
    while (1):
        Input = input("\n" + "我:")
        ans = llm.query(Input)  # 注意，这里是阻塞的
        print(ans)