import pandas as pd
import datetime as dt
import re
import logging

import AfterPostActivity as apa
import ArticleFilter as utl

def screeningByTime_Del() -> pd.DataFrame:
    df_rev_activity = pd.read_csv('data/article_pool_rev.csv')
    df_process_analysis = pd.read_csv('process_analysis.csv')

    for post_id in range(0,3500):
        print(post_id)
        df_article_group = df_process_analysis.loc[lambda df: df['post_id'] == post_id]
        if not apa.articleGroupFilter(df_article_group):
            df_rev_activity = df_rev_activity[ df_rev_activity['post_id'] != post_id ]
            continue
        
        rev_out_of_timezone_idx_list = []
        df_rev_group = df_rev_activity.loc[lambda df: df['post_id'] == post_id]
        for idx, row in df_rev_group.iterrows():
            if not timePeriodSelection(row):
                rev_out_of_timezone_idx_list.append(idx)
        df_rev_activity.drop(rev_out_of_timezone_idx_list, inplace=True)

    df_rev_activity.reset_index(drop=True, inplace=True)
    return df_rev_activity


def timePeriodSelection(row):
    post_time = dt.datetime.strptime(row['post_time'][:10], '%Y-%m-%d')
    rev_time_cutoff = post_time + dt.timedelta(days=31)
    rev_time = dt.datetime.strptime(row['timestamp'][:19], '%Y-%m-%dT%H:%M:%S')
    if rev_time > rev_time_cutoff:
        return False
    else:
        return True


def checking():
    rev_activity_list = pd.read_csv('data/rev_pool_reduced_list.csv')
    counter = 0
    for idx,row in rev_activity_list.iterrows():
        rev_time = dt.datetime.strptime(row['timestamp'][:10], '%Y-%m-%d')
        post_time = dt.datetime.strptime(row['post_time'][:10], '%Y-%m-%d')

        time_delta = rev_time - post_time
        if time_delta.days < -6:
            print(row)

checking() 
# screeningByTime_Del().to_csv('data/rev_pool_reduced_list.csv')