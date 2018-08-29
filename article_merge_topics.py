#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 31 21:55:39 2018

this code is to 
1. merge data with topics
2. place entity tags
3, merge with place entity tags

@author: Ang
"""
import pandas as pd
import numpy as np
from geotext import GeoText

def reTopics(row):
    lst = list(row[['0', '1', '2', '3', '4', '5', '6']])
    if sum(lst) != 0:
        [topic] = sorted(range(len(lst)), key=lambda i: lst[i])[-1:]
    else:
        topic = -1
    return topic
    

def articleTopics():
    data = pd.read_table("/Users/angli/ANG/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEvents&Wikipedia/data/results_v1.csv", 
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
    article_data = pd.read_table("/Users/angli/ANG/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEvents&Wikipedia/data/posted_itn_v3.csv", 
                             sep=',', error_bad_lines = False)
    article_data_zh = article_data[['zh_title', 'article', 'header']]
    article_data_zh=article_data_zh.rename(columns = {'zh_title':'title'})
    
    article_data_es = article_data[['es_title', 'article', 'header']]
    article_data_es=article_data_es.rename(columns = {'es_title':'title'})
    
    article_data_en = article_data[['article', 'header']]
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

#place entity tags
def reCities(row):
    text = row['header'] + " " + row['article']
    text = text.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`–~-=_+"})
    places = GeoText(text)
    lst_cities = list(places.cities) 
    #lst_contries = list(places.country_mentions) 
    return ":".join(lst_cities)

def reContries(row):
    text = row['header'] + " " + row['article']
    text = text.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`–~-=_+"})
    places = GeoText(text)
    #lst_cities = list(places.cities) 
    lst_contries = list(places.country_mentions) 
    return ":".join(lst_contries)


def prossData():
    ##process data              
    process_data = pd.read_table("/Users/angli/ANG/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEvents&Wikipedia/data/process_analysis.csv", 
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

#for places
article_data['city'] = article_data.apply(reCities, axis = 1) 
article_data['contry'] = article_data.apply(reContries, axis = 1) 


#for topics
articleTopics = articleTopics()
articleTopics = articleTopics.drop_duplicates()

#read process data
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
       'year', 'key',  'title', 'header', 'article_key',
       'itn_posted_year', 'itn_posted_time', 'topic', 'city', 'contry']]

process_data_topic = process_data_topic.drop_duplicates()

process_data_topic = process_data_topic.loc[process_data_topic['RD']==False]

process_data_topic.to_csv("/Users/angli/ANG/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEvents&Wikipedia/data/process_data_with_topic_location.csv")

#get the location               
Location_data = process_data_topic[[ 'post_id', 'language', 'title', 'header', 'article', 'city', 'contry']]

Location_data = Location_data.drop_duplicates()

def genLink(row):
    title = row['title']
    title_link = "https://en.wikipedia.org/wiki/"+title
    return title_link
    
def countryDict():
    contry_code = pd.read_csv("/Users/angli/ANG/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEvents&Wikipedia/data/countryCodes.csv",encoding = "ISO-8859-1")
    contrycode_dict = pd.Series(contry_code['countryNames'].values, index=contry_code['contry']).to_dict()
    contrycode_dict['NA'] = "Namibia"
    contrycode_dict['EC'] = "Ecuador"
    return contrycode_dict

contrycode_dict = countryDict()
def contryName(row):
    contry_code = row['contry']
    contry_lst = []
    
    if contry_code != "":
        contry_code_lst = contry_code.split(':')        
        
        for code in contry_code_lst:
            if code != "":
                contry_name = contrycode_dict[code]
                contry_lst.append(contry_name)
    
    contry_names = ":".join(contry_lst)
    return contry_names


Location_data["article_link"] = Location_data.apply(genLink, axis = 1) 
Location_data["country_name"] = Location_data.apply(contryName, axis = 1) 


Location_data.to_csv("/Users/angli/ANG/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEvents&Wikipedia/data/Location_data.csv")




