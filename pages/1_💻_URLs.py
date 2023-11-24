# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 14:22:14 2023

@author: shangfr
"""
import re
import asyncio
import streamlit as st
from html_parser import get_docs, aload

st.title('📖 网页解析监控')

@st.cache_data
def parser_urls(urls,inner):
    output = []
    for url in urls: 
        output.extend(get_docs(url,inner))
    return output

if 'html' not in st.session_state:
    st.session_state['urls'] = set(["https://www.susallwave.com"])
    st.session_state['html'] = []
    st.session_state['url_text'] = "https://www.susallwave.com"

def get_links():
    links = st.session_state['url_text'].strip().replace(" ", "").split("\n")
    links = [k for k in links if len(k)>5]
    if links:
        st.session_state['urls'] = st.session_state['urls'].union(set(links))

with st.sidebar:
    with st.expander("编辑URL"):
        url = st.text_area(
            'URL',key="url_text",on_change=get_links, help='https://github.com/shangfr/Feed-Monitoring-Tool')

    if st.session_state['urls']:    
        urls = st.session_state['urls']
        options = st.multiselect(
            'URL选择',
            urls, urls)
        
        
        on = st.toggle('Activate playwright',value=True)
        inner = st.toggle('Analyze internal links',value=True)

        st.caption("Starting load HTML documents from a list of URLs…了解[Playwright](https://playwright.dev/python/)")
        cola,colb = st.columns([2,1])
        if options and cola.button("解析网页", use_container_width=True):
            if on:
                loop = asyncio.ProactorEventLoop()
                asyncio.set_event_loop(loop)
                st.session_state['html'].extend(loop.run_until_complete(aload(options,inner=inner)))
            else:
                st.session_state['html'].extend(parser_urls(options,inner=inner))

                st.info("解析已完成！")

        if colb.button("清空", use_container_width=True):
            st.cache_data.clear()
            st.session_state['urls'] = set()
            st.session_state['html'] = []
            st.toast('Reset!', icon='🆑')


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
    st.info("👈1. 编辑URL; \n\n👈2. 选择要解析的URL; \n\n👈3. 点击解析按钮。")
    

    