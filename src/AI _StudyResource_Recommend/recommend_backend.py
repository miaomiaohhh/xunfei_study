from flask_cors import CORS
from flask import Flask, request
import os
from spark_ai_recommend import ai_recommend  # 确保这个函数能够处理传入的文本和主题

# 创建服务器
app = Flask(__name__)
CORS(app)


# 定义路由，用于接收文本并生成PPT
@app.route('/generate_ppt', methods=['POST'])
def generate_from_text():
    # 获取POST请求中的文本和主题
    data = request.get_json()
    if not data or 'text' not in data:
        return 'Missing text or theme or is_card_note in the request', 400

    response = ai_recommend(data)

    # generate_ppt 应该返回生成的PPT的信息，或者一些指示信息
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
