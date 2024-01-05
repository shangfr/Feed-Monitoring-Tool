# -*- coding: utf-8 -*-
"""
Created on Fri Jan  5 13:11:15 2024

@author: 86155
"""

import redis

pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)
r.set('food', 'mutton', ex=3)
print(r.get('food'))


print(r.set('fruit', '2watermelon', nx=True))# True--不存在
print(r.get('fruit'))

news_count_key = 'news_count'
news_count = r.get(news_count_key)
if not news_count:
    news_count = 0

news_key = 'news_list'
news_list = r.hgetall(news_key)
# 获取哈希表中的所有键
keys = r.hgetall(news_key)
news_list = []
# 遍历键，获取每个键对应的值
for key in keys:
    news_item = await r.hgetall(key)
    news_list.append(news_item)
    
    
# 获取所有键
all_keys = r.keys()
 
# 打印所有键及其相关的值
for key in all_keys:
    value = r.get('https://36kr.com/feed-newsflash')
    print("Key: {}, Value: {}".format(key, value))
    
# Get all members of the 'news_keys' set
news_keys = r.smembers('https://36kr.com/feed-newsflash')
url_uuid = r.lrange("http://news.baidu.com/n?cmd=4&class=cba&tn=rss", 0, -1)

news = []
for uuid in url_uuid:
    #info = {}
    #info["title"] = r.hget(uuid,"title")
    info = r.hgetall(uuid)
    news.append(info)
        
    
    
# 获取奇数索引的元素（从0开始计数）
news_url = r.lrange("news_count", 0, -1)[::2]
# 获取偶数索引的元素（从0开始计数）
news_cnt = r.lrange("news_count", 0, -1)[1::2]

news_cnt = [int(x) for x in news_cnt]
# 使用sum()函数求和
total = sum(news_cnt)

#r.flushdb()
    


    
    
    