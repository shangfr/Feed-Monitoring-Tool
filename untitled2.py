# -*- coding: utf-8 -*-
"""
Created on Fri Jan  5 15:52:06 2024

@author: 86155
"""

import asyncio
import aioredis

# 连接到 Redis
r = aioredis.Redis(host='localhost', port=6379, db=0)

# 异步函数来存储新闻列表


async def store_news_list(news_list, news_key):
    # 清空现有的新闻列表
    await r.delete(news_key)

    # 将新的新闻添加到列表中
    for news_item in news_list:
        # 假设每个新闻项是一个字典
        news_item_title = news_item['title']  # 使用新闻标题作为键
        news_item_details = news_item  # 新闻详情作为值
        # 将新闻详情存储为哈希表
        await r.hset(news_item_title, news_item_details)

# 调用异步函数


async def main():
    # 这是你的新闻列表
    news_list = [
        {"title": "News Title 1", "summary": "Summary 1",
            "author": "Author 1", "publish_time": "2023-04-01T12:00:00Z"},
        {"title": "News Title 2", "summary": "Summary 2",
            "author": "Author 2", "publish_time": "2023-04-02T12:00:00Z"},
        # ...更多新闻
    ]

    # 存储新闻列表
    news_key = 'news_list'
    await store_news_list(news_list, news_key)

# 运行异步主函数
asyncio.run(main())
