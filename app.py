# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 18:00:28 2023

@author: shangfr
"""

import asyncio
import streamlit as st

from utils import fetchfeeds, pd_func


st.set_page_config(page_title="监控APP", layout="wide")

st.title('🎙️ 资讯实时监控')
st.markdown(
    """
<style>
button {
    height: auto;
    padding-top: 10px !important;
    padding-bottom: 10px !important;
}
</style>
""", unsafe_allow_html=True)


def start_stop(flag):
    st.session_state.run = flag


def clear_reset():
    st.session_state['feeds'] = []
    st.session_state.run = False


if 'feeds' not in st.session_state:
    st.session_state['feeds'] = []
    st.session_state.run = False


with st.sidebar:
    rss_txt = st.text_area(
        'Feed', '''https://36kr.com/feed-newsflash\nhttps://www.zhihu.com/rss''')
    kw_txt = st.text_input('关键词', '科技 风险 绿色')
    contents = st.multiselect('监控内容', ['title', 'summary'], 'title')
    feedurls = rss_txt.split("\n")
    keywords = kw_txt.split(" ")

    INTERVAL = st.number_input('时间间隔(s)', 5, step=5)

cola, colb = st.columns([1, 9])

tab0, tab1 = colb.tabs(["📈 状态", "🗃 详情"])

with cola:
    st.markdown('')
    st.markdown('')
    st.button('🚗', on_click=start_stop, kwargs={
              'flag': True}, disabled=st.session_state.run,help="开始")
    st.button('⛔️', on_click=start_stop, kwargs={
              'flag': False}, disabled=not st.session_state.run)
    st.button('🆑', on_click=clear_reset, disabled=st.session_state.run)
    st.button('🔁', disabled=not st.session_state.run)

with tab0.expander("Stats", expanded=True):
    placeholder0 = st.empty()
    placeholder1 = st.empty()
    placeholder2 = st.empty()


parm_dict = {"feeds": st.session_state['feeds'],
             "feedurls": feedurls,
             "keywords": "|".join(keywords),
             "contents": contents
             }
st_show = [placeholder0, placeholder1, placeholder2]

feeds_num = len(st.session_state['feeds'])
placeholder0.progress(feeds_num % 100, text=f"📝 匹配到`{feeds_num}`条信息")
placeholder1.info("**关键词**：" + kw_txt +
                  "\n\n**监控区域**：" + "\n".join(contents))
placeholder2.info("**RSS**：\n\n> - " + "\n\n> - ".join(feedurls))

with tab1:
    if feeds_num > 0:
        #placeholder3.success("- "+"\n\n- ".join([f['title'] for f in st.session_state['feeds'][-3:]]))
        df, dfa, srs_max = pd_func(st.session_state['feeds'])

        st.subheader("网站统计")
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
                     }, hide_index=True)

        st.subheader("数据详情")
        st.dataframe(df,
                     column_config={
                         "link": st.column_config.LinkColumn(
                             "links",
                             max_chars=100,
                         )
                     }, use_container_width=True, hide_index=True)
    else:
        st.write("👈 `启动`🚗后，点击`更新`🔁按钮查看最新数据。")


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(fetchfeeds(st.session_state.run, parm_dict, st_show))
