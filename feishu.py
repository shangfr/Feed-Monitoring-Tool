# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 10:15:46 2023

@author: shangfr
"""
import requests

def push_report(web_hook, info, at_all=False):
    
    if len(info['summary'])>3000:
        info['summary'] = info['summary'][:3000]
        
    if at_all:
        info['summary'] = info['summary']+"<at id=all></at>"

    header = {
        "Content-Type": "application/json;charset=UTF-8"
    }
    message_body = {
        "msg_type": "interactive",
        "card": {
            "config": {
                "wide_screen_mode": True
            },
            "card_link": {
                "url": info['link']

            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": info['summary']
                },
                {
                    "elements": [
                        {
                            "content": f"💡 点击查看详情，新闻发布于 {info['published'].split(' ')[1]}",
                            "tag": "plain_text"
                        }
                    ],
                    "tag": "note"
                }
            ],
            "header": {
                "template": "wathet",
                "title": {
                    "content": info['title'],
                    "tag": "plain_text"
                }
            }
        }
    }

    ChatRob = requests.post(url=web_hook, json=message_body, headers=header)
    opener = ChatRob.json()
    print("opener:{}".format(opener))
    if opener["StatusMessage"] == "success":
        print(f"{opener} 通知消息发送成功！")
    else:
        print(f"通知消息发送失败，原因：{opener}")


if __name__ == '__main__':

    web_hook = "https://open.feishu.cn/open-apis/bot/v2/hook/b578df38-bd4a-4257-84bd-3c69920edfa8"

    import feedparser 
    rss_web = feedparser.parse("https://i.scnu.edu.cn/sub")
    rss_web.version
    from utils import rss2dict
    info = rss2dict(rss_web)['feeds'][0]


    push_report(web_hook, info, at_all=False)
