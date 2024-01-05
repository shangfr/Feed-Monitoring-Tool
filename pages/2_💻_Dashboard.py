# -*- coding: utf-8 -*-
"""
Created on Mon Dec 25 11:01:26 2023

@author: shangfr
"""
import streamlit as st
from analysis import matching_cnt

st.set_page_config(page_title="网络信息监控APP", layout="wide", page_icon="👨‍💻")
st.title('👨‍💻 监控大屏')


st.markdown("""
<style>
h2 {text-align: center;}
img {width: 100%;height: 100%;}
</style>
""", unsafe_allow_html=True)


results = st.session_state['results']
###############################################################################
cola, colb = st.columns([2, 1])
if results.get("news"):
    news = results["news"]
    df, df_count1 = matching_cnt(news)
    df_count2 = df_count1.groupby('source').sum()
    df_count3 = df_count1.groupby('reading').sum()

    max_va = df_count2['matches'].sum()
    max_vb = df_count2['total'].sum()

###############################################################################

    cola, colb = st.columns([3, 2])
    cola.dataframe(
        df_count2,
        column_config={
            "matches": st.column_config.ProgressColumn(
                "Number of matches",
                help="Number of matching news",
                format="%d ⭐",
                min_value=0,
                max_value=int(max_va),
            ),
            "total": st.column_config.ProgressColumn(
                "Total number of news",
                help="Total number of news",
                format="%d ⭐",
                min_value=0,
                max_value=int(max_vb),
            ),
        },use_container_width=True,hide_index=False,
    )

    cola.bar_chart(df_count3)
    
    colb.dataframe(df_count1,height=500,hide_index=True)

    with st.expander("🚀 详情"):
        st.dataframe(df,
                     column_config={
                         "link": st.column_config.LinkColumn(
                             "links",
                             max_chars=100,
                         )
                     }, use_container_width=True, hide_index=True)


    cola, colb = st.columns([2, 1])
    select_type = colb.selectbox('类型', ["全部","匹配"])
    source_lst = results['source']
    
    if source := cola.selectbox('数据源', source_lst):
        news_source = [item for item in news if item['source'] == source]
        if select_type == "匹配":
            news_source = [item for item in news if item['match']]

        #news_info_lst = [f"[{info['title']}]({info['link']}) ⭐\n\n{info['summary'][:120]}" if info['match'] else f"[{info['title']}]({info['link']})\n\n{info['summary'][:120]}" for info in news_source]
        news_info_lst = [f"[{info['title']}]({info['link']}) ⭐`{info['match']}`\n\n{info['summary'][:120]}".replace("⭐``","") for info in news_source]
        
        news_info = "- "+"\n\n- ".join(news_info_lst)
        
        st.markdown(f"{news_info}", unsafe_allow_html=True)

else:
    st.info("👈 启动🚗后，点击更新🔁按钮查看最新数据。")









   

