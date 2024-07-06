from flask_cors import CORS
from flask import Flask, request, jsonify
import regex
import os
import sys
import random
from ..utils import Logger
from ..spark.SparkApi import SparkLLM
#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#print(sys.path)
import json5

with open('./config.json', encoding='utf-8') as f:
    config = json5.load(f)
appid = config['appid']
api_secret = config['api_secret']
api_key = config['api_key']

domain = "generalv3.5"    # v3.0版本
Spark_url = "wss://spark-api.xf-yun.com/v3.5/chat"  # v3.5环服务地址

# 创建服务器
app = Flask(__name__)
CORS(app)

# 创建SparkLLM对象
llm = SparkLLM(appid, api_key, api_secret, Spark_url, domain, False)

get_subjects_prompt = ''' 我以以下格式: {
   	"parent_subjects": ["math","微积分","积分"],
       "aready_subjects": ["曲面积分"]
   } 给你提供一个有关学科科目的json，请你根据里面的信息以我指定的格式: {
   	"subjects" ["定积分","不定积分"]
   } 返回其中包含在parent_subjects的最后一个subject下的除aready_subjects外的其他知识点。
   提供给你的json如下, 请直接返回json, 不要添加任何其他描述:'''
get_problems_prompt = '''我以以下格式:
        {
                "subjects": "数学计算" /*问题考察的知识点*/, 
            "count": 3 /*要求提供的题目数量, 不要少于此数量*/,
            "min_difficulty": 3 /*1-10*/,
            "max_difficulty": 8 /*1-10*/,
            "type": ["单选题", "填空题", "判断题"], /*需要的题目类型, 不要给出这里所提到的类型这之外的题目*/
                "others": "希望能出一些计算量比较大的题目"
        }
        给你提供一个对于试题描述的json，请你根据里面的信息以我指定的格式:
        {
                "problems": [
                    {
                        "type": "single_choice" /*注意注意type只能为single_choice, judgement或fillin, 不要给出这之外的类型*/,
                        "problem": "1+1=( )",
                        "choices": ["1","2","3","4"],
                        "answer": [1] /*对应上一个的下标, 通过这里判断单选多选*/,
                        "analysis": "一个很简单的数学题"
                    },
                    {
                        "type": "fillin" /*填空、主观等填写的题目*/,
                        "problem": ["1+2=","4+5=","请回答"], /*以空为分隔符分隔，最后即时没字符也应该有一个结束字符串*/
                        "answer": ["3", "9"] /*几个空几个答案*/,
                        "analysis": "可以化为2进制去计算"
                    },
                    {
                        "type": "judgement",
                        "problem": "6+7=11",
                        "answer": false,
                        "analysis": "可以按计算器"
                    }
                ]
            }
        返回其要求的试题数据。注意只返回5道单选，5道判断，5道填空题。但如果试题描述的"others"要求了题型和题目数量则按照"others"生成题目。
        提供给你的json如下, 请直接返回json, 不要添加任何其他描述:'''
get_classtestproblems_prompt = '''我以以下格式:
        {
                "subjects": "数学计算" /*问题考察的知识点*/, 
            "count": 3 /*要求提供的题目数量, 不要少于此数量*/,
            "min_difficulty": 3 /*1-10*/,
            "max_difficulty": 8 /*1-10*/,
            "type": ["单选题", "填空题", "判断题"], /*需要的题目类型, 不要给出这里所提到的类型这之外的题目*/
                "others": "希望能出一些计算量比较大的题目"
        }
        给你提供一个对于试题描述的json，请你根据里面的信息以我指定的格式:
        {
                "problems": [
                    {
                        "type": "single_choice" /*注意type只能为single_choice, judgement或fillin, 不要给出这之外的类型*/,
                        "problem": "1+1=( )",
                        "choices": ["1","2","3","4"],
                        "answer": [1] /*对应上一个的下标, 通过这里判断单选多选*/,
                        "analysis": "一个很简单的数学题"
                    },
                    {
                        "type": "fillin" /*填空、主观等填写的题目*/,
                        "problem": ["1+2=","4+5=","请回答"], /*以空为分隔符分隔，最后即时没字符也应该有一个结束字符串*/
                        "answer": ["3", "9"] /*几个空几个答案*/,
                        "analysis": "可以化为2进制去计算"
                    },
                    {
                        "type": "judgement",
                        "problem": "6+7=11",
                        "answer": false,
                        "analysis": "可以按计算器"
                    }
                ]
            }
        返回其要求的试题数据。注意默认只返回3道单选、3道判断、3道填空题，但如果试题描述的"others"要求了题型和题目数量则按照"others"生成题目。
        提供给你的json如下, 请直接返回json, 不要添加任何其他描述:'''
get_evaluation_prompt1 = '''我以以下两个格式: 
   {
        "problems": [
            {
                "type": "choice" /*这里可以不区分多选单选*/,
                "problem": "1+1=( )",
                "choices": ["1","2","3","4"],
                "answer": [1] /*对应上一个的下标, 通过这里判断单选多选*/,
                "analysis": "一个很简单的数学题"
            },
            {
                "type": "completion" /*填空、主观等填写的题目*/,
                "problem": ["1+2=","4+5=","请回答"], /*以空为分隔符分隔，最后即时没字符也应该有一个结束字符串*/
                "answer": ["3", "9"] /*几个空几个答案*/,
                "analysis": "可以化为2进制去计算"
            },
            {
                "type": "judgement",
                "problem": "6+7=11",
                "answer": false,
                "analysis": "可以按计算器"
            }
        ]
    },
    {
        "answers": [
            [1],
            ["2","9"],
            [false]
        ]
    }
    给你提供一个题目的json1和用户答案的json2，请你根据里面的信息以我指定的格式: {
    	"evaluation": "还不错, 但有一些马虎的错误, 还有十足的进步空间" /*对用户作答情况的描述, 此处只是个请你依据实际情况描述, 不要少于15字*/,
    	"knowledge_radar": {
    		"dimension": ["概念","计算","求导","积分","导数","基础"], /*雷达图的维度, 你需要根据题目的json分析出应该包含哪些维度(6维), 而不是和示例一样, 并进行打分*/
            "score": [100,80,30,10,10,40]
    	},
        "shortcoming": "不会求导" /*缺点*/,
        "suggestion": "多练练求导" /*意见*/
    }
    返回对用户作答情况和学习情况的解析json。
    给你的题目json1如下: '''
get_evaluation_prompt2 = '''\n给你的用户答案json2如下: '''
get_evaluation_prompt3 = '''\n请直接返回解析json, 不要添加任何其他描述:'''

@app.route('/get_subjects', methods=['POST'])
def get_subjects_handler():
    content = request.json
    question = get_subjects_prompt + str(content)
    ans = llm.query(question)
    ans = ans[ans.find('{'): ans.rfind('}')+1]
    Logger.info(ans)
    return ans

@app.route('/get_problems', methods=['POST'])
def get_problems_handler():
    content = request.json
    Logger.info(content)
    """
    {
    "subjects": ["math","chinese"],
   	"time": 10 /*mins*/,
   	"min_difficulty": 3 /*1-10*/,
   	"max_difficulty": 8,
   	"type": ["single_choice", "judgement"],
    "others": "希望能出一些计算量比较大的题目"
   }
    """
    subjects = content['subjects']
    time = content['time']
    types = content['type']
    str_types = ['"'+x+'"' for x in types]
    cnt = max(len(subjects), int(time / 3))
    rest = len(subjects)
    ans = {'problems': []}
    for subject in subjects:
        rest -= 1
        now_cnt = random.randint(1, cnt - rest)
        cnt -= now_cnt
        json_str = f'''{{
        "subjects": "{subject}" /*问题考察的知识点*/,
        "count": {now_cnt} /*要求提供的题目数量, 不要少于此数量或多于此数量*/,
        "min_difficulty": {content['min_difficulty']} /*1-10*/,
        "max_difficulty": {content['max_difficulty']} /*1-10*/,
        "type": {str_types} /*需要的题目类型, 不要给出这里所提到的类型这之外的题目*/, 
        "others": "{content['others']}" /*其他要求*/
        }}'''
        Logger.info(f'json_str:{json_str}')
        question = get_problems_prompt + json_str
        ans_str = llm.query(question)
        ans_str = ans_str[ans_str.find('{'): ans_str.rfind('}') + 1]
        # Logger.info(f'ans_str:{ans_str}')
        now_ans = json5.loads(ans_str)
        ans['problems'].extend(now_ans['problems'])
        
    Logger.info(ans)
    return jsonify(ans)  # 确保返回的是JSON格式

@app.route('/get_ClassTestProblems', methods=['POST'])
def get_classtestproblems_handler():
    content = request.json
    Logger.info(content)
    """
    {
    "subjects": ["math","chinese"],
   	"time": 10 /*mins*/,
   	"min_difficulty": 3 /*1-10*/,
   	"max_difficulty": 8,
   	"type": ["single_choice", "judgement"],
    "others": "希望能出一些计算量比较大的题目"
   }
    """
    subjects = content['subjects']
    time = content['time']
    types = content['type']
    str_types = ['"'+x+'"' for x in types]
    cnt = max(len(subjects), int(time / 3))
    rest = len(subjects)
    ans = {'problems': []}
    for subject in subjects:
        rest -= 1
        now_cnt = random.randint(1, cnt - rest)
        cnt -= now_cnt
        json_str = f'''{{
        "subjects": "{subject}" /*问题考察的知识点*/,
        "count": {now_cnt} /*要求提供的题目数量, 不要少于此数量或多于此数量*/,
        "min_difficulty": {content['min_difficulty']} /*1-10*/,
        "max_difficulty": {content['max_difficulty']} /*1-10*/,
        "type": {str_types} /*需要的题目类型, 不要给出这里所提到的类型这之外的题目*/, 
        "others": "{content['others']}" /*其他要求*/
        }}'''
        Logger.info(f'json_str:{json_str}')
        question = get_classtestproblems_prompt + json_str
        ans_str = llm.query(question)
        ans_str = ans_str[ans_str.find('{'): ans_str.rfind('}') + 1]
        # Logger.info(f'ans_str:{ans_str}')
        now_ans = json5.loads(ans_str)
        ans['problems'].extend(now_ans['problems'])
        
    Logger.info(ans)
    return jsonify(ans)  # 确保返回的是JSON格式

@app.route('/get_evaluation', methods=['POST'])
def get_evaluation_handler():
    content = request.json
    Logger.info(content)
    """
    {
        "json1": {
            "problems": [
                {
                    "type": "choice" /*这里可以不区分多选单选*/,
                    "problem": "1+1=( )",
                    "choices": ["1","2","3","4"],
                    "answer": [1] /*对应上一个的下标, 通过这里判断单选多选*/,
                    "analysis": "一个很简单的数学题"
                },
                {
                    "type": "completion" /*填空、主观等填写的题目*/,
                    "problem": ["1+2=","4+5=","请回答"], /*以空为分隔符分隔，最后即时没字符也应该有一个结束字符串*/
                    "answer": ["3", "9"] /*几个空几个答案*/,
                    "analysis": "可以化为2进制去计算"
                },
                {
                    "type": "judgement",
                    "problem": "6+7=11",
                    "answer": false,
                    "analysis": "可以按计算器"
                }
            ]
        },
        "json2": {
            "answers": [
                [1],
                ["2","9"],
                [false]
            ]
        }
    }
    """
    json1 = content['json1']
    json2 = content['json2']
    question = get_evaluation_prompt1 + str(json1) + get_evaluation_prompt2 + str(json2) + get_evaluation_prompt3
    ans = llm.query(question)
    ans = ans[ans.find('{'): ans.rfind('}') + 1]
    Logger.info(ans)
    return ans

@app.route('/submit_test', methods=['POST'])
def submit_test():
    data = request.json
    # 处理接收到的数据
    print(data)
    transformed_data = transform_data(data)
    print(transformed_data)
    json1 = transformed_data['problems']
    json2 = transformed_data['answers']
    question = get_evaluation_prompt1 + str(json1) + get_evaluation_prompt2 + str(json2) + get_evaluation_prompt3
    ans = llm.query(question)
    ans = ans[ans.find('{'): ans.rfind('}') + 1]
    print(ans)
    return ans

def transform_data(data):
    transformed_problems = []
    extracted_answers = []

    # Process single_choice_problems
    for problem in data.get('single_choice_problems', []):
        transformed_problem = {
            "type": "choice",
            "problem": problem["problem"],
            "choices": problem["choices"],
            "answer": problem["answer"],
            "analysis": problem["analysis"]
        }
        doneanswer = problem.get('doneanswer')
        if doneanswer is not None:
            extracted_answers.append(doneanswer)
        transformed_problems.append(transformed_problem)

    # Process fillin_problems
    for problem in data.get('fillin_problems', []):
        transformed_problem = {
            "type": "completion",
            "problem": problem["problem"],
            "answer": problem["answer"],
            "analysis": problem["analysis"]
        }
        doneanswer = problem.get('doneanswer')
        if doneanswer is not None:
            extracted_answers.append(doneanswer)
        transformed_problems.append(transformed_problem)

    # Process judgement_problems
    for problem in data.get('judgement_problems', []):
        transformed_problem = {
            "type": "judgement",
            "problem": problem["problem"],
            "answer": problem["answer"],
            "analysis": problem["analysis"]
        }
        doneanswer = problem.get('doneanswer')
        if doneanswer is not None:
            extracted_answers.append(doneanswer)
        transformed_problems.append(transformed_problem)

    return {
        "problems": transformed_problems,
        "answers": extracted_answers
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
