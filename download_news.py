# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 17:38:58 2023

@author: shangfr
"""
import uuid
import feedparser
import async_timeout
import aiohttp
import asyncio
import aioredis

from dateutil import parser
from datetime import datetime

namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')

def string_to_timestamp(time_str):
    #time_str = "Thu, 21 Dec 2023 11:20:17 +0800"
    #time_str = "2023-12-21 13:01:41  +0800"
    #time_str = "Wed, 20 Dec 2023 10:56:44 GMT"
    #time_str = "2023-12-21T11:20:17"

    try:
        dt = parser.parse(time_str)
        standard_time_format = dt.strftime("%Y-%m-%d %H:%M:%S")

    except ValueError as e:
        standard_time_format = time_str
        print(f"\nError parsing the date: {e}\n")

    #timestamp = int(dt.timestamp())
    return standard_time_format


def parse_feed(html):
    """
    feed信息格式化
    """
    rss_data = feedparser.parse(html)

    '''
    关键词 = 'example'
    filtered_entries = [entry for entry in rss_data.entries if 关键词 in entry.title or 关键词 in entry.content[0].value]
    '''

    # 获取当前时间
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if rss_data.get('feed').get('title'):
        source = rss_data.feed.title
    else:
        source = '无'

    item = {'title': '',
            'summary': '',
            'content': '',
            'author': '',
            "source": source,
            'link': '',
            'published': '',
            'date': now
            }

    news = []

    # feed parsing
    for fd in rss_data.entries:
        if 'title' in fd.keys():
            item["title"] = fd.title

        if 'summary' in fd.keys():
            summary = fd.summary
            if len(summary)>1000:
                summary = summary[:1000]
            item["summary"] = summary

        if 'link' in fd.keys():
            item["link"] = fd.link

        if 'published' in fd.keys():
            date_str = fd.published
            item["published"] = string_to_timestamp(date_str)

        text = item['title']+"\n\n"+item['summary']
        item['uuid'] = str(uuid.uuid3(namespace, text))
        news.append(item.copy())

    return news


async def fetch_url(url):
    async with aiohttp.ClientSession() as session:
        async with async_timeout.timeout(20):
            try:
                async with session.get(url) as response:
                    return await response.text()
            except:
                return ''



async def add_news(news,url):
    
    news_count = 0
    for news_detail in news:
        news_key = news_detail['uuid']
        if not await r.exists(news_key):

            await r.hset(news_key, mapping=news_detail)
            await r.lpush(url, news_key)
            news_count += 1 
    if news_count:
        await r.rpush("news_count",url, news_count)
        print(f"Total news added: {news_count}_{url}")
        


async def fetch_and_parse(url):
    
    html = await fetch_url(url)
    if html:
        #print(f"\nParsing {url}")
        news = await asyncio.to_thread(parse_feed, html)
        #print(f"\nFinished parsing {url},get {len(news)} news.")
        await add_news(news,url)
        #print(f"\nFinished {url} add_news")
    else:
        await r.sadd("error_urls",url)
        await r.expire('error_urls', 3600)    
        print(f"\nERROR --- Fetching {url}")


def read_rss(dtype="最新"):
    import pandas as pd
    df = pd.read_csv("data/rss.csv")
    urls = df.loc[df['类型'] == dtype, "RSS"].tolist()
    return urls

# 异步主函数，用于并发获取和解析所有URL的内容
async def main():
    
    # 定义要获取的URL列表
    urls = read_rss(dtype="最新")
    feed_urls = ['https://www.zhihu.com/rss',
                 'https://36kr.com/feed-newsflash',
                 'https://rss.shab.fun/cctv/world']
    feed_urls.extend(urls)

    error_urls = await r.smembers("error_urls")

    feed_urls = [url for url in feed_urls if url not in error_urls]
   
    tasks = [fetch_and_parse(url) for url in feed_urls]
    #tasks = [asyncio.create_task(fetch_and_parse(url)) for url in urls]
    print(f"任务数：{len(tasks)}")
    await asyncio.gather(*tasks)
    await r.close()
# spyder 调试
# import nest_asyncio
# nest_asyncio.apply()

# 运行异步主函数
print(f"执行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
r = aioredis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
asyncio.run(main())
