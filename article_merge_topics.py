#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 31 21:55:39 2018

@author: Ang
"""
import pandas as pd

data = pd.read_table("/Users/Ang/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEvents&Wikipedia/data/results_v1.csv", 
                         sep=',', error_bad_lines = False)

data.columns.values

article_set1 = data[['article', '0', '1', '2', '3', '4', '5', '6']]
article_set2 = data[['article2', '0', '1', '2', '3', '4', '5', '6']]
article_set2=article_set2.rename(columns = {'article2':'article'})

article_set = pd.concat([article_set1, article_set2], ignore_index=True)

#set key 
article_set_drop = article_set.drop(article_set[article_set.article == ' '].index).reset_index(drop=True)
article_set_drop['article'] = article_set_drop['article'].str.replace(r'<!--.+?-->', '', case=False)
set_article_lsts = list(article_set_drop['article'])
set_article_lsts = [s.strip("`~()?:!.,;'""&*<=+ >#|-/{}%$^@[]") for s in set_article_lsts]
set_article_lsts = [s.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`–~-=_+"}) for s in set_article_lsts]
set_article_lsts = [s.replace(" ", '').lower() for s in set_article_lsts]
article_set_drop['key'] = set_article_lsts                              
  

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
article_data_lsts = list(article_data['article'])
article_data_lsts = [s.strip("`~()?:!.,;'""&*<=+ >#|-/{}%$^@[]") for s in article_data_lsts]
article_data_lsts = [s.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`–~-=_+"}) for s in article_data_lsts]
article_data_lsts = [s.replace(" ", '').lower() for s in article_data_lsts]
article_data['key'] = article_data_lsts                              

#merge article with topics
article_data_topic = article_data.merge(article_set_drop, on = 'key', how = 'left')
article_data_topic = article_data_topic.drop_duplicates()
                 

##process data              
process_data = pd.read_table("/Users/Ang/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEvents&Wikipedia/data/process_analysis.csv", 
                         sep=',', error_bad_lines = False)
process_data['article'] = process_data['article'].str.replace(r'<!--.+?-->', '', case=False)
process_data_lsts = list(process_data['article'])
process_data_lsts = [s.strip("`~()?:!.,;'""&*<=+ >#|-/{}%$^@[]") for s in process_data_lsts]
process_data_lsts = [s.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`–~-=_+"}) for s in process_data_lsts]
process_data_lsts = [s.replace(" ", '').lower() for s in process_data_lsts]
process_data['key'] = process_data_lsts                              
