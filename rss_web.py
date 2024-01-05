# -*- coding: utf-8 -*-
"""
Created on Thu Dec 28 17:09:34 2023

@author: shangfr
"""
import requests
import pandas as pd
from bs4 import BeautifulSoup


def update_rss():
    
    #feed = f"http://news.baidu.com/n?cmd={row['cmd']}&class={row['class']}&tn=rss"
    url = "https://www.baidu.com/search/rss.html"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.text.encode(response.encoding).decode('gb2312')
        
        soup = BeautifulSoup(data, 'html.parser')
        li_tags = soup.find_all('li')
        
        # 提取列表内容
        extracted_list = [item.get_text(strip=True) for item in li_tags]
        extracted_link = [item.find('input')['value']
                          for item in li_tags if item.find('input')]
        
        extracted_list = extracted_list[0:len(extracted_link)]
        type_list = ["焦点" if "焦点" in item else "最新" for item in extracted_list]
        extracted_list = [item.split("焦点")[0] if "焦点" in item else item.split("最新")[0] for item in extracted_list]
        df = pd.DataFrame({"类型": type_list, "名称": extracted_list, "RSS": extracted_link})
        
        df.to_csv("data/rss.csv", index=False)
        print(f"更新成功！共{df.shape[0]}个。")
    else:
        print("更新失败！")


def read_rss(dtype="最新"):
    df = pd.read_csv("data/rss.csv")
    urls = df.loc[df['类型'] == dtype, "RSS"].tolist()
    return urls



