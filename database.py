# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 17:38:58 2023

@author: shangfr
"""
import sqlite3
import feedparser
import async_timeout
import aiohttp
import asyncio
from dateutil import parser
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name, timeout=100)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        # 创建用户表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            created_at DATE NOT NULL
        )
        ''')

        # 创建新闻表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            news_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            summary TEXT,
            content TEXT,
            author TEXT,
            source TEXT NOT NULL,
            link TEXT,
            published TEXT,
            date  TEXT,
            category TEXT,
            keywords TEXT,
            UNIQUE (title, source)
        )
        ''')

        # 创建用户与新闻的交互表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_news_interaction (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            news_id INTEGER,
            read BOOLEAN NOT NULL,
            liked BOOLEAN NOT NULL,
            shared BOOLEAN NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (news_id) REFERENCES news (news_id)
        )
        ''')


        # 创建大模型对新闻的判断
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS news_qa (
            id INTEGER PRIMARY KEY,
            news_id INTEGER,
            llm_name TEXT,
            question TEXT NOT NULL,
            answer TEXT,
            FOREIGN KEY (news_id) REFERENCES news (news_id) ON DELETE CASCADE
        )
        ''')
        
        # 创建每日新闻统计表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS news_stats (
            date DATE PRIMARY KEY,
            views INTEGER NOT NULL,
            likes INTEGER NOT NULL,
            shares INTEGER NOT NULL
        )
        ''')

        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def insert_news(self, news_data):
        # 将新闻数据插入到数据库中
        self.cursor.execute('INSERT OR IGNORE INTO news (title, summary, content, author, source, link, published, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                            tuple(news_data))
        self.conn.commit()

    def insert_dict_news(self, dict_data):
        # 将新闻数据插入到数据库中

        field_names = list(dict_data.keys())
        values = list(dict_data.values())

        self.cursor.execute("INSERT OR IGNORE INTO news ({}) VALUES ({})".format(
            ','.join(field_names), ','.join(['?'] * len(values))), values)
        self.conn.commit()

    def insert_user(self, user_data):
        # 将用户数据插入到数据库中
        self.cursor.execute('INSERT OR IGNORE INTO users (username, password, email, created_at) VALUES (?, ?, ?, ?)',
                            tuple(user_data))
        self.conn.commit()

    def insert_user_news_interaction(self, user_news_interaction_data):
        # 将用户与新闻的交互数据插入到数据库中
        # 查找用户与新闻的交互数据
        self.cursor.execute('SELECT * FROM user_news_interaction WHERE user_id = ? AND news_id = ?',
                            (user_news_interaction_data[0], user_news_interaction_data[1]))
        interaction = self.cursor.fetchone()
        # 如果存在，则更新数据
        if interaction:
            self.cursor.execute('UPDATE user_news_interaction SET read = ?, liked = ?, shared = ? WHERE user_id = ? AND news_id = ?',
                                tuple(user_news_interaction_data))
            self.conn.commit()
        else:
            # 如果不存在，则插入新的数据
            self.cursor.execute('INSERT INTO user_news_interaction (user_id, news_id, read, liked, shared) VALUES (?, ?, ?, ?, ?)',
                                tuple(user_news_interaction_data))
            self.conn.commit()

    def insert_news_qa(self, qa_data):

        field_names = list(qa_data.keys())
        values = list(qa_data.values())

        self.cursor.execute("INSERT INTO news_qa ({}) VALUES ({})".format(
            ','.join(field_names), ','.join(['?'] * len(values))), values)
        self.conn.commit()

            
    def select_news(self, news_id):
        # 从数据库中查询新闻
        self.cursor.execute('SELECT * FROM news WHERE news_id = ?', (news_id,))
        news_data = self.cursor.fetchone()
        return news_data

    def select_user(self, user_id):
        # 从数据库中查询用户
        self.cursor.execute(
            'SELECT * FROM users WHERE user_id = ?', (user_id,))
        user_data = self.cursor.fetchone()
        return user_data

    def select_user_news_interaction(self, user_id, news_id):
        # 从数据库中查询用户与新闻的交互
        self.cursor.execute(
            'SELECT * FROM user_news_interaction WHERE user_id = ? AND news_id = ?', (user_id, news_id))
        user_news_interaction_data = self.cursor.fetchone()
        return user_news_interaction_data

    def delete_news(self, news_id):
        # 从数据库中删除新闻
        self.cursor.execute('DELETE FROM news WHERE news_id = ?', (news_id,))
        self.conn.commit()

    def delete_user(self, user_id):
        # 从数据库中删除用户
        self.cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        self.conn.commit()


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
        print(f"Error parsing the date: {e}")

    #timestamp = int(dt.timestamp())
    return standard_time_format


async def parse_feed(html):
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
            item["summary"] = fd.summary

        if 'link' in fd.keys():
            item["link"] = fd.link

        if 'published' in fd.keys():
            date_str = fd.published
            item["published"] = string_to_timestamp(date_str)
        
        
        news.append(item.copy())

    return news


async def fetch_url(url):
    async with aiohttp.ClientSession() as session:
        async with async_timeout.timeout(10):
            try:
                async with session.get(url) as response:
                    return await response.text()
            except:
                return ''


async def fetch_and_parse(url):
    # 使用DatabaseManager类
    db_manager = DatabaseManager('test.db')
    db_manager.create_tables()

    html = await fetch_url(url)
    if html:
        news = await parse_feed(html)
        print(f"Finished parsing {url}")
        for d in news:
            db_manager.insert_dict_news(d)
    else:
        print(f"ERROR --- Fetching {url}")

    db_manager.close()


# 异步主函数，用于并发获取和解析所有URL的内容
async def main():
    # 定义要获取的URL列表
    feed_urls = ['https://36kr.com/feed-newsflash',
                 'https://www.zhihu.com/rss',
                 'https://rss.shab.fun/cctv/world']

    # 并发获取和解析每个URL的内容
    tasks = [fetch_and_parse(url) for url in feed_urls]
    #tasks = [asyncio.create_task(fetch_and_parse(url)) for url in urls]
    await asyncio.gather(*tasks)

# spyder 调试
# import nest_asyncio
# nest_asyncio.apply()

# 运行异步主函数
asyncio.run(main())
