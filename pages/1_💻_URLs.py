# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 14:22:14 2023

@author: shangfr
"""
import re
import asyncio
import streamlit as st
from html_parser import get_docs, aload

st.title('📖 网页解析监控[Playwright](https://playwright.dev/python/)')

@st.cache_data
def parser_urls(url):
    return get_docs(url)

if 'html' not in st.session_state:
    st.session_state['html'] = []
    st.session_state['urls'] = []
with st.sidebar:
    url = st.text_area(
        'URL', '''https://www.susallwave.com\nhttps://www.163.com/dy/article''', help='https://github.com/shangfr/Feed-Monitoring-Tool')
    
    on = st.toggle('Activate playwright')
    
    if url:
        if st.button("获取网页"):
            links = url.strip().replace(" ", "").split("\n")
            links = list(set(links))
            
            if on:
                st.session_state['urls'] = links
            else:
                docs = []
                for u in links:    
                    docs.extend(parser_urls(u))
                    
                st.session_state['html'] = docs
                st.session_state['urls'] = [dt["metadata"]["source"] for dt in docs]
        
        urls = st.session_state['urls']
        options = st.multiselect(
            'URL选择',
            urls, urls)

        st.caption("Starting load HTML documents from a list of URLs…")

        if st.button("解析网页"):
            if on:
                loop = asyncio.ProactorEventLoop()
                asyncio.set_event_loop(loop)
                st.session_state['html'] = loop.run_until_complete(aload(urls))
            else:
                st.info("解析已完成！")
                

html = st.session_state['html']
results = []

if html:
    col0, col1 = st.columns([5, 1])
    color = col1.color_picker('关键词标记', '#00f900')
    kw_txt = col0.text_input('关键词筛选', '科技 风险 绿色', help="使用空格分割")
    keywords = [t for t in kw_txt.split(" ") if t]

    for dt in html:
        if re.search("|".join(keywords), dt['page_content']):
            results.append(dt["metadata"]["source"])
    
            for keyword in keywords:
                replacement = f"<font color={color}>{keyword}</font>"
                dt['page_content'] = re.sub(keyword, replacement, dt['page_content'])

if results:
    sc = st.selectbox("选择", results)
    htm = [h for h in html if h["metadata"]["source"] == sc][0]
    with st.expander("查看"):
        st.markdown(htm['page_content'], unsafe_allow_html=True)
else:
    st.warning("无")