# -*- coding: utf-8 -*-
"""
Created on Mon Dec 25 11:01:26 2023

@author: shangfr
"""
import streamlit as st
from analysis import matching_cnt

st.set_page_config(page_title="网络信息监控APP", layout="wide", page_icon="👨‍💻")
st.title('👨‍💻 监控大屏')


st.markdown('''<style>

h2 {text-align: center;}
img {width: 100%;height: 100%;}

[data-testid="stDataFrameResizable"] {
        border: 2px solid rgba(250, 250, 250, 0.1) !important;
}
</style>''', unsafe_allow_html=True)


results = st.session_state['results']

if results.get("news"):
    news = results["news"]
    #df, dfa, df_count = data_cnt(news)
    df, df_count1 = matching_cnt(news)
    df_count2 = df_count1.groupby('source').sum()
    st.dataframe(df_count2.style.highlight_max(props='font-weight:bold;color:#e83e8c'),use_container_width=True)

    cola, colb = st.columns([2, 1])
    select_type = colb.selectbox('类型', ["全部","匹配"])
    source_lst = results['source']
    
    if source := cola.selectbox('数据源', source_lst):
        news_source = [item for item in news if item['source'] == source]
        if select_type == "匹配":
            news_source = [item for item in news if item['match']]

        #news_info_lst = [f"[{info['title']}]({info['link']}) ⭐\n\n{info['summary'][:120]}" if info['match'] else f"[{info['title']}]({info['link']})\n\n{info['summary'][:120]}" for info in news_source]
        news_info_lst = [f"[{info['title']}]({info['link']}) ⭐`{info['match']}`\n\n".replace("⭐``","") for info in news_source]
        
        news_info = "- "+"\n\n- ".join(news_info_lst)
        
        st.markdown(f"{news_info}", unsafe_allow_html=True)

    with st.expander("🚀 详情"):
        st.dataframe(df,
                     column_config={
                         "link": st.column_config.LinkColumn(
                             "links",
                             max_chars=100,
                         )
                     }, use_container_width=True, hide_index=True)

else:
    st.info("👈 启动🚗后，点击更新🔁按钮查看最新数据。")