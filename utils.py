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

    rss_data = feedparser.parse(html)
    feedslist = feed2dict(rss_data)
    for info_dict in feedslist:
        for cn in parm_dict['contents']:
            if re.search(parm_dict['keywords'], info_dict[cn]):
                if info_dict not in parm_dict['feeds']:
                    parm_dict['feeds'].append(info_dict)
                    break


async def fetch(session, url):
    async with async_timeout.timeout(10):
        try:
            async with session.get(url) as response:
                return await response.text()
        except:
            return ''


async def fetchfeeds(run, parm_dict, st_show=[]):

    seconds = 0
    INTERVAL = 5

    while run:

        for url in parm_dict['feedurls']:
            async with aiohttp.ClientSession() as session:
                html = await fetch(session, url)
                if html:
                    await check_rss(html, parm_dict)
                else:
                    url = " Error 😭 解析错误 "+url

            if st_show:
                feeds_num = len(parm_dict['feeds'])
                titles = "- "+"\n\n- ".join([f"{info['web']} [{info['title']}]({info['link']})"
                                            for info in parm_dict['feeds'][-3:]])

                st_show[0].progress(feeds_num %
                                    100, text=f"📝 匹配到`{feeds_num}`条信息")
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
    df['date'] = pd.to_datetime(df['published'], utc=True).dt.date
    del df['published']
    del df['summary']

    def date_cnt(srs):
        return srs.value_counts().tolist()

    dfa = df.groupby('web').agg(
        {"title": "count", "date": date_cnt}).reset_index()

    dfa.columns = ['web', 'title', 'match_history']

    srs_max = dfa['match_history']
    for i in range(len(srs_max)):
        srs_max = max(srs_max)

    return df, dfa, srs_max


def feed2dict(rss_data):
    """
    feed信息格式化
    """

    if rss_data.get('feed').get('title'):
        web_name = rss_data.feed.title
    else:
        web_name = ''

    item = {"web": web_name,
            'title': '',
            'link': '',
            'summary': '',
            'published': ''
            }

    feedslist = []

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

    return feedslist
