# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 13:10:13 2024

@author: shangfr
"""
import streamlit as st
from feishu import push_report


cola, colb = st.columns([1, 2])
placeholder0 = st.empty()


results = st.session_state['results']
news = results["news"]

source_lst = list(set([t['source'] for t in news]))
if source := cola.selectbox('数据源', source_lst):
    news_source = [n for n in news if n['source'] == source]
    tlt_lst = [t['title'] for t in news_source]
    if tlt := colb.selectbox('选择消息', tlt_lst):
        info = news_source[tlt_lst.index(tlt)]
        #with placeholder0.expander(f"", expanded=True):
        placeholder0.markdown(f"{info['summary']} [查看详情]({info['link']})", unsafe_allow_html=True)

        if web_hook := st.text_input("推送地址", ""):
            with st.expander("⚙️ 设置", expanded=True):
                colx0, colx1, colx2, colx3, colx4, colx5 = st.columns(6)
            parms = {"title": colx0.toggle("标题", value=True),
                     "summary": colx1.toggle("摘要", value=True),
                     "link": colx2.toggle("链接", value=True),
                     "published": colx3.toggle("日期", value=True),
                     "web": colx4.toggle("网站"),
                     "at_all": colx5.toggle("@ALL")}
            # Every form must have a submit button.
            submitted = st.button(
                "发送", type="primary", use_container_width=True)

            if submitted:
                
                push_report(web_hook, info, parms)
                st.success("消息发送成功！")