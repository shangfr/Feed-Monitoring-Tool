# -*- coding: utf-8 -*-
"""
Created on Tue Dec 26 16:13:21 2023

@author: shangfr
"""
import pandas as pd

def ts2lst(ts_lst):
    if ts_lst:
        time_series = pd.to_datetime(ts_lst)
        return time_series.to_frame().resample('H').size().tolist()
    else:
        return [0,0,0]

def df_cnt(df0):
    df = df0.copy()
    df['reading'] = df['reading'].str[10:16]
    
    dfa = df.groupby(["reading",'source','mtype']).agg({'match': ['count']}).reset_index()
    dfa.columns = ["reading",'source','mtype','count']
    df_count = dfa.pivot(index=['reading','source'],columns='mtype', values='count').reset_index()
    df_count.fillna(0,inplace=True)
    if df['mtype'].nunique() == 2:
        df_count['total'] = df_count['not']+df_count['match']
    else:
        df_count['total'] = df_count.iloc[:,-1]
        df_count['match'] = 0
    return df_count

def data_cnt(news):
    df = pd.DataFrame(news)
    #df['published'] = pd.to_datetime(df['published'])
    df['mtype'] = "match"
    df.loc[df['match']=='','mtype'] = "not"
        
    df_resample = df.groupby(['source','mtype']).agg({'match' : ['count'],'published':[list]}).reset_index()
    df_resample.columns = ['source','mtype','count','published']
    
    df_count = df_resample.pivot(index='source',columns='mtype', values=['count','published']).reset_index()
    
    if len(df_count.columns) == 3:
        df_count.columns = ['source','total',"total_history"]
        df_count['match'] = 0
        df_count["match_history"] = 0

    else:
        cols = ['source','match','total',"match_history","total_history"]
        df_count.columns = cols
    
    df_count.fillna(0,inplace=True)
    
    df_count["total_history"] = df_count["total_history"].apply(ts2lst)
    df_count["match_history"] = df_count["match_history"].apply(ts2lst)

    df_count['total'] = df_count['total']+df_count['match']

    new_columns = ['source','match',"match_history",'total',"total_history"]

    dfa = df_cnt(df)
    return df,dfa,df_count[new_columns]

def matching_cnt(news):

    df = pd.DataFrame(news)

    df['reading'] = pd.to_datetime(df['reading']).dt.strftime("%Y-%m-%d %H:%M")
    df['mtype'] = 1
    df.loc[df['match']=='','mtype'] = 0

    df_count=df[["reading",'source','mtype']].groupby(["reading",'source']).agg(['sum','count']).reset_index()
    df_count.columns = ["reading",'source','matches','total']

    return df,df_count
    
    
