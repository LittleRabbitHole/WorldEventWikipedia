import pandas as pd
import datetime as dt
import re
import logging

import AfterPostActivity as apa
import ArticleFilter as utl

def screeningByTime_Del() -> pd.DataFrame:
    df_rev_activity = pd.read_csv('data/article_pool_rev.csv')
    df_process_analysis = pd.read_csv('/Users/keyangzheng/Google Drive/WorldEvents&Wikipedia/data/process_data_with_topic.csv')

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


def addMissingData():
    df_rev_activity = pd.read_csv('data/rev_pool_reduced_list.csv')
    df_process_analysis = pd.read_csv('/Users/keyangzheng/Google Drive/WorldEvents&Wikipedia/data/process_data_with_topic.csv')
    df_rev_activity_full = df_rev_activity
    rev_headers = ['revid','user','timestamp','size','comment','tags']

    for post_id in range(0,3500):
        print(post_id)
        df_article_group = df_process_analysis.loc[lambda df: df['post_id'] == post_id]
        if not apa.articleGroupFilter(df_article_group):
            # df_rev_activity = df_rev_activity[ df_rev_activity['post_id'] != post_id ]
            continue
        
        df_rev_group = df_rev_activity.loc[lambda df: df['post_id'] == post_id]
        lang_rev = {'en': False, 'cn': False, 'es': False}
        lang_articles = df_article_group['language'].tolist()
        for idx,row in df_rev_group.iterrows():
            lang_rev[row['language']] = True
        
        missing_lang = []
        for key in lang_rev.keys():
            if (key in lang_articles) and (not lang_rev[key]):
                missing_lang.append(key)
        
        for idx,row in df_article_group.iterrows():
            if row['language'] not in missing_lang:
                continue
        
            #get data
            start_day = dt.datetime.strptime(row['First edit time'][:10], '%Y-%m-%d')

            post_day = dt.datetime.strptime(str(row['year']) + " " + row['time'], '%Y %B %d') if int(row['time_from_post']) < 0 else start_day

            end_day = post_day + dt.timedelta(days=31)

            rv_list = apa.getRVRawData(row['article'], row['language'], old=start_day, new=end_day)
            
            if len(rv_list) <= 0:
                continue
            
            rev_data_list = []
            for rev in rv_list:
                entry = {}
                entry['post_id'] = row['post_id']
                entry['language'] = row['language']

                entry['article_id'] = row['ID']

                entry['post_time'] = dt.datetime.strptime(str(row['year']) + ' ' + row['time'], '%Y %B %d').isoformat()
                entry['category'] = row['category']
                entry['topic'] = row['topic']

                for key in rev_headers:
                    if key in rev.keys():
                        entry[key] = rev[key]
                    else:
                        # logger.warn('article: ' + row['article'] + ' revision: ' + str(rev['revid']) + ' missing key: ' + key)
                        entry[key] = ''
                
                entry['wiki_links'] = row['Links from this page']
                entry['external_links'] = row['External links']
                entry['references'] = row['References']

                rev_data_list.append(entry)
            
            df_rev_activity_full = pd.concat([df_rev_activity_full, pd.DataFrame(rev_data_list)], ignore_index=True)
        
    return df_rev_activity_full

        


# checking() 
# screeningByTime_Del().to_csv('data/rev_pool_reduced_list.csv')
addMissingData().to_csv('data/rev_pool.csv')
