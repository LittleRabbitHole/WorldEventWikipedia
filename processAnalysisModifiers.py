###
# Set of functions related to manipulating the process_analysis.csv dataset 
###

import pandas as pd
import re
import datetime as dt


process_analysis = pd.read_csv('process_analysis.csv', squeeze=True)
df_itn = pd.read_csv('itns copy.csv')
posted_itn = pd.read_csv('posted_itn_n.csv')

process_analysis['year'] = process_analysis['year'].apply(str)

def recentDeathFilter():
    process_analysis['RD'] = process_analysis.apply(checkRecentDeath, axis=1)

# has errors !! DO NOT USE !!
def checkRecentDeath(row):
    article_field = 'article'
    if row['language'] == 'cn':
        article_field = 'zh_title'
    elif row['language'] == 'es':
        article_field = 'es_title'
    article_title = row.at['article']
    print(article_title)
    itn = posted_itn.loc[posted_itn[article_field] == article_title]
    # itn.sort_index(inplace=True)
    print(itn['header'])
    post_header = itn.at[0,'header']
    print(post_header)
    original_itn = df_itn.loc[df_itn['header'] == post_header]
    rd_field = original_itn['recentdeaths']
    rd_indicator = ['death of', 'Death of', '[RD]', 'RD:', 'RD']
    is_rd = False
    for indicator in rd_indicator:
        if indicator in post_header:
            is_rd = True
            break
    if rd_field is 'no':
        is_rd = False
    
    return is_rd

def timeFromPost():
    process_analysis['time_from_post'] = process_analysis.apply(timeFromPostCalcuator, axis=1)
    # pass

def timeFromPostCalcuator(row):
    if row['time_from_post'] == 0:
        post_time = dt.datetime.strptime(row['year'] + ' ' + row['time'], '%Y %B %d')
        article_creation_time = dt.datetime.strptime(row['First edit time'], '%Y-%m-%d %H:%M')
        time_delta = (article_creation_time - post_time).days
        return time_delta
    else: 
        return row['time_from_post']

def saveData(data: pd.DataFrame, path: str):
    data.to_csv(path)


# recentDeathFilter()
timeFromPost()
saveData(process_analysis, 'process_analysis_n.csv')
