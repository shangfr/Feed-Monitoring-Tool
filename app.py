# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 18:00:28 2023

@author: shangfr
"""

import asyncio
import streamlit as st
from html_parser import clean_url
from utils import fetchfeeds, pd_func


st.set_page_config(page_title="监控APP", layout="wide", page_icon="🚗")

st.title('🚗 资讯实时监控')
st.markdown(
    """
<style>
button {
    height: auto;
    padding-top: 10px !important;
    padding-bottom: 10px !important;
}

h2 {text-align: center;}
img {width: 100%;height: 100%;}
</style>
""", unsafe_allow_html=True)


def start_stop(flag):
    st.session_state.run = flag
    if flag:
        st.toast('Start!', icon='🚗')
    else:
        st.toast('Stop!', icon='⛔️')


def clear_reset():
    st.session_state['feeds'] = []
    st.session_state.run = False
    st.toast('Reset!', icon='🆑')


def update_dt():
    st.toast('Data Update!', icon='🔁')


if 'feeds' not in st.session_state:
    st.session_state['feeds'] = []
    st.session_state.run = False


with st.sidebar:

    search = st.toggle('Feed or Search', help="Feed: 推送源  Search:搜索")
    if search:
        feedurls = []
        st.success("👉点击🚗启动关键词定时搜索")

    else:
        st.info("👇输入Feed源，👉点击🚗启动")
        rss_txt = st.text_area(
            'Feed', '''https://36kr.com/feed-newsflash\nhttps://www.zhihu.com/rss\nhttps://rss.shab.fun/cctv/world''', help='https://github.com/shangfr/Feed-Monitoring-Tool')

        feedurls = [clean_url(t)
                    for t in rss_txt.replace(" ", "").split("\n") if t]
    kw_txt = st.text_input('关键词', '科技 风险 绿色', help="使用空格分割")
    contents = st.multiselect('监控内容', ['title', 'summary'], 'title')
    INTERVAL = st.number_input('时间间隔(s)', 5, step=5)

    using_llm = st.toggle('LLM Monitoring', help="使用大模型进行内容监控")
    if using_llm:
        st.success("👇🤖 启动LLM Monitoring [Agent](https://github.com/shangfr/MRKL-AgentBot)")


cola, colb = st.columns([1, 9])

tab0, tab1, tab2 = colb.tabs(["📈 状态", "🗃 详情", "🤖 推送"])

with cola:
    st.markdown('')
    st.markdown('')
    st.button('🚗', on_click=start_stop, kwargs={
              'flag': True}, disabled=st.session_state.run, help="开始")
    st.button('⛔️', on_click=start_stop, kwargs={
              'flag': False}, disabled=not st.session_state.run)
    st.button('🆑', on_click=clear_reset, disabled=st.session_state.run)
    st.button('🔁', on_click=update_dt, disabled=not st.session_state.run)

with tab0.expander("Stats", expanded=True):
    placeholder0 = st.empty()
    placeholder1 = st.empty()
    placeholder2 = st.empty()


parm_dict = {"feeds": st.session_state['feeds'],
             "feedurls": feedurls,
             "keywords": kw_txt,
             "contents": contents
             }
st_show = [placeholder0, placeholder1, placeholder2]
feeds_num = len(st.session_state['feeds'])
placeholder0.progress(feeds_num % 100, text=f"📝 匹配到`{feeds_num}`条信息")
placeholder1.info("**关键词**：" + kw_txt +
                  "\n\n**监控区域**：" + "\n".join(contents))
if feedurls:
    placeholder2.info("**RSS**：\n\n> - " + "\n\n> - ".join(feedurls))

with tab1:
    if feeds_num > 0:
        #placeholder3.success("- "+"\n\n- ".join([f['title'] for f in st.session_state['feeds'][-3:]]))
        df, dfa, srs_max = pd_func(st.session_state['feeds'])
        with st.expander("网站统计"):
            st.dataframe(dfa,
                         column_config={
                             "web": "Web name",
                             "title": st.column_config.NumberColumn(
                                 "Number of news",
                                 help="Number of news",
                                 format="%d ⭐",
                             ),
                             "match_history": st.column_config.LineChartColumn(
                                 "Views (past 30 days)", y_min=0, y_max=srs_max
                             ),
                         }, use_container_width=True, hide_index=True)

        with st.expander("数据详情"):
            st.dataframe(df,
                         column_config={
                             "link": st.column_config.LinkColumn(
                                 "links",
                                 max_chars=100,
                             )
                         }, use_container_width=True, hide_index=True)
        cola.download_button(
            label="🚀",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name='table.csv',
            mime='text/csv',
            key="table",
            help="Download data"
        )

    else:
        st.info("👈 启动🚗后，点击更新🔁按钮查看最新数据。")


with tab2:
    from feishu import push_report
    colx0, colx1, colx2, colx3, colx4, colx5 = st.columns(6)
    parms = {"title": colx0.toggle("标题", value=True),
             "summary": colx1.toggle("摘要", value=True),
             "link": colx2.toggle("链接", value=True),
             "published": colx3.toggle("日期", value=True),
             "web": colx4.toggle("网站"),
             "at_all": colx5.toggle("@ALL")}
    feeds = st.session_state['feeds']
    tlt_lst = [t['title'] for t in feeds]
    if tlt := st.selectbox('选择消息', tlt_lst):
        info = feeds[tlt_lst.index(tlt)]
        with st.expander(f"{info['web']} [查看详情]({info['link']})"):
            st.markdown(f"{info['summary']}", unsafe_allow_html=True)

        if web_hook := st.text_input("推送地址", ""):
            # Every form must have a submit button.
            submitted = st.button("发送", type="primary", use_container_width=True)
    
            if submitted:
                push_report(web_hook, info, parms)
                st.success("消息发送成功！")


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(fetchfeeds(st.session_state.run, parm_dict, st_show))
st.stop()
