# -*- coding: utf-8 -*-
"""
Created on Mon Dec 25 11:01:26 2023

@author: shangfr
"""
import asyncio
import streamlit as st
from collections import defaultdict


st.set_page_config(page_title="网络信息监控APP", layout="wide", page_icon="👨‍💻")

st.write('''
<style>
button {
    height: auto;
    padding-top: 10px !important;
    padding-bottom: 10px !important;
}

[data-testid="column"] {
    width: calc(20% - 1rem) !important;
    flex: 1 1 calc(20% - 1rem) !important;
    min-width: calc(20% - 1rem) !important;
}
</style>''', unsafe_allow_html=True)


st.title('👨‍💻Feed订阅信息实时监控')

@st.cache_data
def agent(prompt = ''):

    return ""

import redis

pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)


news_url = r.lrange("news_count", 0, -1)[::2]
news_cnt = r.lrange("news_count", 0, -1)[1::2]
news_cnt = [int(x) for x in news_cnt]
urls = list(set(news_url))
total = sum(news_cnt)


with st.sidebar:
   #st.info("👉点击🚗启动监控程序")

    keywords = st.text_input('关键词', '(绿色|低碳|减排|减碳)',
                             help="使用正则表达式，格式：(关键词1|关键词2)")
    col1, col2 = st.columns([2, 1])
    monitoring = col1.multiselect('监控内容', ['标题', '摘要'], ['标题', '摘要'])
    interval = col2.number_input('自动更新(s)', 10, 36000, 10, step=10)

    using_llm = st.toggle('LLM Monitoring', help="使用大模型进行内容监控")

    if using_llm:
        st.success(
            "👇🤖 启动LLM Monitoring [Agent](https://github.com/shangfr/MRKL-AgentBot)")
        prompt = st.text_area('监控需求', '请监控人工智能相关的新闻舆情', help="语言描述监控需求")
    else:
        prompt = ''


if 'results' not in st.session_state:
    st.session_state['results'] = defaultdict(list)
    st.session_state.run = False
    st.session_state.task_run = False


def run_state(flag):
    if flag == "start":
        st.session_state.run = True
        st.toast('Start!', icon='🚗')
    elif flag == "stop":
        st.session_state.run = False
        st.toast('Stop!', icon='⛔️')
    elif flag == "reset":
        st.session_state['results'] = defaultdict(list)
        st.session_state.run = False
        st.toast('Reset!', icon='🆑')
    elif flag == "update":
        st.toast('Data Update!', icon='🔁')


col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

col1.button('🚗 开始', on_click=run_state, kwargs={
            'flag': "start"}, disabled=st.session_state.run, use_container_width=True, help="开始")
col2.button('⛔️ 暂停', on_click=run_state, kwargs={
            'flag': "stop"}, disabled=not st.session_state.run, use_container_width=True)
col3.button('🆑 重置', on_click=run_state, kwargs={
            'flag': "reset"}, disabled=st.session_state.run, use_container_width=True)
col4.button('🔁 更新', on_click=run_state, kwargs={
            'flag': "update"}, disabled=not st.session_state.run, use_container_width=True)


results = st.session_state['results']
#tab0, tab1, tab2 = st.tabs(["📈 状态", "🗃 数据", "🤖 推送"])
###############################################################################

with st.expander("📈 状态", expanded=True):
    placeholder0 = st.empty()
    placeholder1 = st.empty()
 
placeholder2 = st.empty()

results = st.session_state['results']
feeds_num = len(results['uuid_set'])
if feeds_num == 0:
    placeholder0.progress(
        feeds_num % 100, text=f"📝 `{len(urls)}`个数据源，👆🚗 启动后，点击更新🔁按钮查看最新数据\n\n")
    placeholder1.info(f"**关键词**：{keywords}\n\n**监控区域**：" + "\n".join(monitoring) +
                      f"\n\n**自动更新间隔**： {str(interval)}秒")
    placeholder2.info(
        f"**RSS({len(urls)})**：\n\n> - " + "\n\n> - ".join(urls[-5:]))
else:

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

    placeholder0.progress(match_news_num % 100, text=ph0)
    placeholder1.success(ph1)
    placeholder2.markdown(ph2)

monitoring_dict = {'标题': 'title', '摘要': 'summary'}


parm_dict = {
    "keywords": keywords,
    "monitoring": [monitoring_dict.get(m) for m in monitoring],
    "prompt": prompt,
    "results": st.session_state['results']
}

st_show = [placeholder0, placeholder1, placeholder2]
st_run = st.session_state["run"]

from utils import display_status,fetch_and_parse
async def fetch_query_results(urls, run=False, interval=5,st_show=[], **kwargs):
    print(f"启动--{run}")
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
        
        await asyncio.sleep(5)
        print(f"complete--{run}")


print(f"task_run---{st.session_state.task_run}")
print(f"st_run-----{st_run}")

if st.session_state.task_run and st_run:
    st.stop()

st.session_state.task_run = st_run
asyncio.run(fetch_query_results(urls, st_run, interval, st_show, **parm_dict))
st.stop()


    

