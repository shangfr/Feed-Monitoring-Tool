# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 18:24:15 2023

@author: shangfr
"""
import re
import feedparser
import async_timeout
import asyncio
import aiohttp

async def check_rss(html, parm_dict):

    rss_web = feedparser.parse(html)
    if rss_web.get('feed').get('title'):
        web_name = rss_web.feed.title
    else:
        web_name = ''
    for entry in rss_web['entries']:
        for cn in parm_dict['contents']:
            if re.search(parm_dict['keywords'], entry[cn]):

                info_dict = {"web":web_name,'title': entry['title'], 'link': entry['link'],
                             'summary': entry['summary'], 
                             'published': entry['published']}

                if info_dict not in parm_dict['feeds']:
                    parm_dict['feeds'].append(info_dict)
                    break


async def fetch(session, url):
    async with async_timeout.timeout(10):
        async with session.get(url) as response:
            return await response.text()


async def fetchfeeds(run, parm_dict, st_show = []):

    seconds = 0
    INTERVAL = 5

    while run:

        for url in parm_dict['feedurls']:
            async with aiohttp.ClientSession() as session:
                html = await fetch(session, url)

                await check_rss(html, parm_dict)

            if st_show:
                feeds_num = len(parm_dict['feeds'])
                titles = "- "+"\n\n- ".join([news['title'] for news in parm_dict['feeds'][-3:]])
                
                
                st_show[0].progress(feeds_num % 100, text=f"📝 匹配到`{feeds_num}`条信息")
                st_show[1].success(f"⏳ Parsing {url}")
                st_show[2].success(titles)


        seconds = seconds + INTERVAL
        await asyncio.sleep(INTERVAL)



def rss2dict(rss_data):
    """
    https://github.com/prakasharul/rss2json
    rss atom to parsed json data
    supports google alerts
    """

    item = {}
    feedslist = []
    feed = {}
    feedsdict = {}
    # parsed feed url

    # feed meta data
    feed["status"] = "ok"
    feed["version"] = rss_data.version
    if 'updated' in rss_data.feed.keys():
        feed["date"] = rss_data.feed.updated
    if 'title' in rss_data.feed.keys():
        feed["title"] = rss_data.feed.title
    if 'image' in rss_data.feed.keys():
        feed["image"] = rss_data.feed.image
    feedsdict["data"] = feed

    # feed parsing
    for fd in rss_data.entries:
        if 'title' in fd.keys():
            item["title"] = fd.title

        if 'link' in fd.keys():
            item["link"] = fd.link

        if 'summary' in fd.keys():
            item["summary"] = fd.summary

        if 'published' in fd.keys():
            item["published"] = fd.published

        if 'storyimage' in fd.keys():
            item["thumbnail"] = fd.storyimage

        if 'media_content' in fd.keys():
            item["thumbnail"] = fd.media_content

        if 'tags' in fd.keys():
            if 'term' in fd.tags:
                item["keywords"] = fd.tags[0]["term"]

        feedslist.append(item.copy())

    feedsdict["feeds"] = feedslist

    # return json.dumps(feedsdict, ensure_ascii=False)
    return feedsdict

def pd_func(feeds):
    import pandas as pd
    df = pd.DataFrame(feeds)
    df['date'] = pd.to_datetime(df['published']).dt.date
    del df['published']
    def date_cnt(srs):
        return srs.value_counts().tolist()
    
    dfa = df.groupby('web').agg({"title":"count","date":date_cnt}).reset_index()
    
    dfa.columns = ['web', 'title', 'match_history']

    srs_max = dfa['match_history']
    for i in range(len(srs_max)):
        srs_max = max(srs_max)
        
    return df, dfa, srs_max
        
        