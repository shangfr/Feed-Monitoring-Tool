# -*- coding: utf-8 -*-
"""
Created on Tue Dec 26 16:34:38 2023

@author: shangfr
"""
import zhipuai

zhipuai.api_key = "749276ba8e3f6496ec657abbd2696b7e.kTyPmsMfIenq9eQa"

def zhipu_agent(prompt):
    # 请求模型
    response = zhipuai.model_api.invoke(
        model="chatglm_turbo",
        prompt=[
            {"role": "user", "content": prompt},
            #{"role": "assistant", "content": "我是人工智能助手"},

        ]
    )

    return response['data']['choices'][0]['content']

'''
news = []
info = ''
prompt_tmp = 以表格形式输出：
| 问题 | 回答 | 准确值 |
|------|-----|-------|
其中，准确值为0-10分的数值型，代表回答问题的准确性。
prompt = f"请给出下面新闻的主要内容，并判断是否和人工智能相关。新闻详情：{info}\n\n{prompt_tmp}"
'''

prompt_tmp = "请监控人工智能相关的新闻舆情"
prompt = f"为了满足：{prompt_tmp}，需要监控哪些关键词？直接给出这些关键词，用逗号分割。"
answer = zhipu_agent(prompt)

answer.split("、")
import jieba  

keywords = jieba.extract_tags(answer, topK=10) 
  
# 输出关键词  
print("关键词：", keywords)

import re

pattern = r'\|.*\|'  # 匹配第一个d和最后一个d之间的内容

re.search(pattern, answer)

import pandas as pd
df = pd.read_markdown()

data = [row.strip().split('|') for row in answer.split('\n')]
header = [h.strip() for h in data[0] if h.strip()]
values = [[val.strip() for val in row if val.strip()] for row in data[2:]]

# Create a dictionary from the data
data_dict = {h: v for h, v in zip(header, zip(*values))}

# Create DataFrame
df = pd.DataFrame(data_dict)
