#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 31 21:55:39 2018

@author: Ang
"""
import pandas as pd
import numpy as np

def reTopics(row):
    lst = list(row[['0', '1', '2', '3', '4', '5', '6']])
    if sum(lst) != 0:
        [topic] = sorted(range(len(lst)), key=lambda i: lst[i])[-1:]
    else:
        topic = -1
    return topic
    

def articleTopics():
    data = pd.read_table("/Users/Ang/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEvents&Wikipedia/data/results_v1.csv", 
                             sep=',', error_bad_lines = False)    
    #data.columns.values
    article_set1 = data[['year','time','article', '0', '1', '2', '3', '4', '5', '6']]
    article_set2 = data[['year','time','article2','0', '1', '2', '3', '4', '5', '6']]
    article_set2=article_set2.rename(columns = {'article2':'article'})
    
    article_set = pd.concat([article_set1, article_set2], ignore_index=True)
    
    #set key 
    article_set_drop = article_set.drop(article_set[article_set.article == ' '].index).reset_index(drop=True)
    article_set_drop['article'] = article_set_drop['article'].str.replace(r'<!--.+?-->', '', case=False)
    article_set_drop['article'] = article_set_drop['article'].str.replace(r'!--.+?-->', '', case=False)
    set_article_lsts = list(article_set_drop['article'])
    set_article_lsts = [s.strip("`~()?:!.,;'""&*<=+ >#|-/{}%$^@[]") for s in set_article_lsts]
    set_article_lsts = [s.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`–~-=_+"}) for s in set_article_lsts]
    set_article_lsts = [s.replace(" ", '').lower() for s in set_article_lsts]
    article_set_drop['key'] = set_article_lsts                              
    article_set_drop = article_set_drop.drop(article_set_drop[article_set_drop.article == ''].index).reset_index(drop=True)
    article_set_drop = article_set_drop.drop_duplicates()
    article_set_drop['topic'] = article_set_drop.apply(reTopics, axis = 1)
    article_set_drop = article_set_drop[["key",'year','time',"article", "topic"]]
    article_set_drop = article_set_drop.rename(columns={"year": "itn_posted_year", 'time':'itn_posted_time'})
    return article_set_drop

def allArticles():
    #article alignment
    article_data = pd.read_table("/Users/Ang/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEvents&Wikipedia/data/posted_itn_v3.csv", 
                             sep=',', error_bad_lines = False)
    article_data_zh = article_data[['zh_title', 'article']]
    article_data_zh=article_data_zh.rename(columns = {'zh_title':'title'})
    
    article_data_es = article_data[['es_title', 'article']]
    article_data_es=article_data_es.rename(columns = {'es_title':'title'})
    
    article_data_en = article_data[['article']]
    article_data_en['title'] = article_data[['article']]
    
    article_data = pd.concat([article_data_en, article_data_es, article_data_zh], ignore_index=True)
    article_data = article_data.dropna().reset_index(drop=True)
    
    article_data['article'] = article_data['article'].str.replace(r'<!--.+?-->', '', case=False)
    article_data['article'] = article_data['article'].str.replace(r'!--.+?-->', '', case=False)
    article_data_lsts = list(article_data['article'])
    article_data_lsts = [s.strip("`~()?:!.,;'""&*<=+ >#|-/{}%$^@[]") for s in article_data_lsts]
    article_data_lsts = [s.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`–~-=_+"}) for s in article_data_lsts]
    article_data_lsts = [s.replace(" ", '').lower() for s in article_data_lsts]
    article_data['key'] = article_data_lsts                              
    return article_data


def prossData():
    ##process data              
    process_data = pd.read_table("/Users/Ang/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEvents&Wikipedia/data/process_analysis.csv", 
                             sep=',', error_bad_lines = False)
    process_data['article'] = process_data['article'].str.replace(r'<!--.+?-->', '', case=False)
    process_data['article'] = process_data['article'].str.replace(r'!--.+?-->', '', case=False)
    process_data_lsts = list(process_data['article'])
    process_data_lsts = [s.strip("`~()?:!.,;'""&*<=+ >#|-/{}%$^@[]") for s in process_data_lsts]
    process_data_lsts = [s.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`–~-=_+"}) for s in process_data_lsts]
    process_data_lsts = [s.replace(" ", '').lower() for s in process_data_lsts]
    process_data['key'] = process_data_lsts                              
    return process_data

#merge article with topics
article_data = allArticles()
article_data = article_data.drop_duplicates()
#article_data.to_csv("/Users/Ang/Desktop/article_data.csv")

articleTopics = articleTopics()
articleTopics = articleTopics.drop_duplicates()

process_data = prossData()#key as key


article_data_topic = article_data.merge(articleTopics, on = 'key', how = 'left')
article_data_topic = article_data_topic.drop_duplicates()
article_data_topic = article_data_topic.rename(columns={"key": "article_key"})
key_lst = list(article_data_topic['title'])
key_lst = [s.strip("`~()?:!.,;'""&*<=+ >#|-/{}%$^@[]") for s in key_lst]
key_lst = [s.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`–~-=_+"}) for s in key_lst]
key_lst = [s.replace(" ", '').lower() for s in key_lst]
article_data_topic['key'] = key_lst                              

process_data_topic = process_data.merge(article_data_topic, on = 'key', how = 'left')
process_data_topic["Assessment"].loc[pd.isnull(process_data_topic["Assessment"])] = "???"

process_data_topic = process_data_topic[['(Semi-)automated edits', 'Assessment',
       'Average edits per day', 'Average edits per month',
       'Average edits per user', 'Average edits per year',
       'Average time between edits (days)', 'Bot edits', 'Characters',
       'Editors', 'Edits in the past 30 days',
       'Edits in the past 365 days',
       'Edits made by the top 10% of editors', 'External links',
       'First edit', 'First edit time', 'ID', 'IP edits', 'Latest edit',
       'Latest edit time', 'Links from this page', 'Links to this page',
       'Minor edits', 'Page size', 'Pageviews (60 days)', 'RD',
       'References', 'Reverted edits', 'Sections', 'Templates',
       'Total edits', 'Unique references', 'Words', 'article', 'category',
       'language', 'post_id', 'time', 'time_from_post', 'time_of_creation',
       'year', 'key',  'title', 'article_key',
       'itn_posted_year', 'itn_posted_time', 'topic']]

process_data_topic = process_data_topic.drop_duplicates()

process_data_topic = process_data_topic.loc[process_data_topic['RD']==False]

process_data_topic.to_csv("/Users/Ang/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEvents&Wikipedia/data/process_data_with_topic.csv")
                 
