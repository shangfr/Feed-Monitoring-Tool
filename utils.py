# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 18:24:15 2023

@author: shangfr
"""
import re
import uuid
import aiohttp
import feedparser
import asyncio
import async_timeout
from datetime import datetime
from dateutil import parser

namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')


def extract_datetime(time_str):
    # Tue Dec 26 13:01:27 +0800 2023
    pattern0 = r'[A-Za-z]{3} [A-Za-z]{3} \d{2} \d{2}:\d{2}:\d{2} [+-]\d{4} \d{4}'
    # 匹配"Thu, 21 Dec 2023 11:20:17 +0800"这种格式
    # 匹配"Wed, 20 Dec 2023 10:56:44 GMT"这种格式
    pattern1 = r'[A-Za-z]{3}, \d{1,2} [A-Za-z]{3} \d{4} \d{2}:\d{2}:\d{2}'
    # 匹配"2023-12-21 13:01:41  +0800"这种格式
    # 匹配"2023-12-21T11:20:17"这种格式
    pattern2 = r'\d{4}-\d{2}-\d{2}.{0,2}\d{2}:\d{2}:\d{2}'

    for pattern in [pattern0, pattern1, pattern2]:
        match = re.search(pattern, time_str)
        if match:
            return match.group()

    return ''


def string_to_timestamp(time_str):

    try:
        dt = parser.parse(time_str)
        standard_time_format = dt.strftime("%Y-%m-%d %H:%M:%S")

    except ValueError as e:
        standard_time_format = time_str
        print(f"\nError parsing the date: {e}\n")

    return standard_time_format

def parse_feed(html):
    """
    feed信息格式化
    """
    news = []
    
    rss_data = feedparser.parse(html)
    source = rss_data.get('feed').get('title')
    entries = rss_data.entries
    
    if entries:
        item = {'title': '',
                'summary': '',
                # 'content': '',
                # 'author': '',
                "match": "",
                "source": source,
                'link': '',
                'published': '',
                'reading': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

        # feed parsing
        for fd in entries:
            if 'title' in fd.keys():
                item["title"] = fd.title

            if 'summary' in fd.keys():
                item["summary"] = fd.summary

            text = item['title']+"\n\n"+item['summary']
            item['uuid'] = str(uuid.uuid3(namespace, text))

            if 'link' in fd.keys():
                item["link"] = fd.link

            if 'published' in fd.keys():
                time_str = fd.published
            elif item["summary"]:
                time_str = extract_datetime(item["summary"])
            else:
                time_str = ''
            item["published"] = string_to_timestamp(time_str)
            
            news.append(item.copy())
            
    return news



def parse_html(html='',news=[], **kwargs):
    if html:
        news = parse_feed(html)

    results = kwargs["results"]
    pattern = kwargs["keywords"]
    monitoring = kwargs["monitoring"]
    
    cnt_a,cnt_b = 0,0
    for item in news:
        if item['uuid'] not in results['uuid_set']:
            results['uuid_set'].append(item['uuid'])

            if pattern:
                text = "\n".join([item.get(m) for m in monitoring])
                match = re.search(pattern, text)
                if match:
                    item['match'] = match.group(0)
                    cnt_a += 1
            
            if item['source'] not in results['source']:
                results['source'].append(item['source'])
                
            results["news"].append(item)
            cnt_b += 1

    if cnt_a or cnt_b:
        cnt_index = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        source = item['source']
        results["news_cnt"].append([source, cnt_index, cnt_a, cnt_b])

        #parsing = f"{url}新增{cnt_b}条，满足条件{cnt_a}条。"
        #print(parsing)

        feeds_num = len(results['uuid_set'])
        source_num = len(results['source'])
        
        match_news = [item for item in results['news'] if item['match']]
        match_news_num = len(match_news)
        
        match_source = [item['source'] for item in match_news]
        match_source = list(set(match_source))
        match_source_num = len(match_source)
        
    
        ph0 = f"📝 已获取`{feeds_num}`条信息，匹配到`{len(match_news)}`条信息"
    
        ph1 = f"⏳ `成功获取{source_num}个新闻源，{match_source_num}个匹配源： {'、'.join(match_source)}`"
        
        ph2 =  "\n\n".join([f"⭐`{info['source']}` `{info['match']}`\n\n- [{info['title']}]({info['link']})"
                                    for info in match_news[-20:]])
    
        output = {"show":[ph0,ph1,ph2],"match_news_num":match_news_num}
        return output
    else:
        return None
    


async def fetch_url(url):
    async with aiohttp.ClientSession() as session:
        async with async_timeout.timeout(10):
            try:
                async with session.get(url) as response:
                    return await response.text()
            except:
                return ''

import aioredis
r = aioredis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

async def read_redis(url):
    url_uuid = await r.lrange(url, 0, -1)

    news = []
    for uuids in url_uuid:
        #info = {}
        #info["title"] = r.hget(uuid,"title")
        info = await r.hgetall(uuids)
        info['match'] = ''
        news.append(info)
    return news


async def fetch_and_parse(url,queue, **kwargs):

    html = ""
    news = await read_redis(url)
    output = await asyncio.to_thread(parse_html,html, news, **kwargs)

    await queue.put(output)
    

async def fetch_and_parse2(url,queue, **kwargs):

    html = await fetch_url(url)
    output = None
    
    if html:
        output = await asyncio.to_thread(parse_html, html, **kwargs)

    await queue.put(output)

        
async def display_status(st_show, queue):  
    placeholder0,placeholder1,placeholder2 = st_show
    try:
        while True:
            await asyncio.sleep(0.01)
            output = await queue.get()
            if output:
                ph0,ph1,ph2 = output["show"]
                placeholder0.progress(output["match_news_num"] % 100, text=ph0)
                placeholder1.success(ph1)
                placeholder2.markdown(ph2)
                #print(output)
                #print('Producer: Done')
            queue.task_done()

    except asyncio.CancelledError:
        print('Consumer: Cancelled')

    finally:
        while not queue.empty():
            output = await queue.get()
            if output:
                print(output)
                ph0,ph1,ph2 = output["show"]
                placeholder0.progress(output["match_news_num"] % 100, text=ph0)
                placeholder1.success(ph1)
                placeholder2.markdown(ph2)
            queue.task_done()


async def fetch_query_results(urls, run=False, interval=5,st_show=[], **kwargs):
    while run:

        queue = asyncio.Queue()
        # start the consumer
        display_task = asyncio.create_task(display_status(st_show, queue))
        tasks = [fetch_and_parse(url, queue, **kwargs) for url in urls]

        await asyncio.gather(*tasks)
        await queue.join()
        display_task.cancel()
        # 等待任务实际完成（如果它已经开始执行）
        await display_task

        await asyncio.sleep(interval)
        print(f"complete--{run}")
