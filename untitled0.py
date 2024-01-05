# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 15:58:01 2024

@author: 86155
"""

# SuperFastPython.com
# example of using an asyncio queue with a limited capacity
from random import random
import asyncio
 
# coroutine to generate work
async def producer(queue):
    print('Producer: Running')
    # generate work
    for i in range(2):
        # generate a value
        value = random()
        await asyncio.sleep(0.5)
        # block to simulate work
        
        # add to the queue, may block
        await queue.put(value)
    print('Producer: Done')
 
# coroutine to consume work
async def consumer(queue):
    print('Consumer: Running')
    # consume work
    try:
        while True:
        # get a unit of work
            item = await queue.get()
            await asyncio.sleep(0.5)
            print(f'>got {item}')
            # block while processing
            # mark as completed
            queue.task_done()

    except asyncio.CancelledError:
        print('Consumer: Cancelled')
        # 在这里处理任何必要的清理工作
    finally:
        print('Consumer: Done')
 
# entry point coroutine
async def main():


    queue = asyncio.Queue()
    # start the consumer
    display_task = asyncio.create_task(consumer(queue))
    # create many producers
    producers = [producer(queue) for _ in range(10)]
    # run and wait for the producers to finish
    await asyncio.gather(*producers)
    # wait for the consumer to process all items
    display_task.cancel()
    # 等待任务实际完成（如果它已经开始执行）
    await display_task
    #await asyncio.sleep(1)
     
# start the asyncio program
asyncio.run(main())