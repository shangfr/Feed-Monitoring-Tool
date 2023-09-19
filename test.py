# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 10:54:03 2023

@author: shangfr
"""
import time
import asyncio

# 👇️ call apply()
import nest_asyncio
nest_asyncio.apply()

async def washing1():
    await asyncio.sleep(3)
    print('小朋友的衣服洗完了')

async def washing2(loop):
    await asyncio.sleep(2)
    print('爷爷奶奶的衣服洗完了')
    loop.stop


async def washing3():
    await asyncio.sleep(5)
    print('爸爸妈妈的衣服洗完了')

async def myCoroutine(id):
    process_time = random.randint(1,5)
    await asyncio.sleep(process_time)
    print("Coroutine: {}, has successfully completed after {} seconds".format(id, process_time))

loop = asyncio.new_event_loop()
# 2. 将异步函数加入事件队列
tasks = [
    washing1(),
    washing2(loop),
    washing3(),
]


asyncio.set_event_loop(loop)
startTime = time.time()
# 3.执行队列实践，直到最晚的一个事件被处理完毕后结束
loop.run_until_complete(asyncio.wait(tasks))
# 4.如果不在使用loop，建议使用关闭，类似操作文件的close()函数
loop.close()
endTime = time.time()
print("洗完三批衣服共耗时: ",endTime-startTime)




import random

async def main():
    tasks = []
    for i in range(10):
        tasks.append(asyncio.ensure_future(myCoroutine(i)))

    await asyncio.gather(*tasks)

try:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
finally:
    loop.close()
    
    
    
    
from utils import fetchfeeds    
feeds = []
feedurls = ['https://36kr.com/feed-newsflash','https://www.zhihu.com/rss']
keywords = ['科技','股市','风险','新闻','消息','大']
contents = ['title', 'summary']
parm_dict = {"feeds":feeds,
             "feedurls":feedurls,
             "keywords":"|".join(keywords),
             "contents":contents
    }


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(fetchfeeds(True, parm_dict))


import pandas as pd
df = pd.DataFrame(feeds)
dfa = df['web'].value_counts().reset_index()

    
    