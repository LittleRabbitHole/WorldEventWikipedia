#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 17:02:50 2018

Language link collection for a data frame with article title in English Wikipedia

output data: all_article_langlinks.pkl

<-> https://zh.wikipedia.org/?curid=1543200

@author: angli
"""

import pandas as pd
import os
import datetime
import numpy as np
import urllib.parse
import json
import csv
import os
import sys
import pickle
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def returnJsonCheck(response) -> dict:
    try:
        return response.json()
    except:
        print("ERROR")
        print(response)
        print(response.text)
        sys.exit("json error")
       


def getPageId(lang, title):
    """insert language and article title, output pageid"""
    
    api = "https://{}.wikipedia.org/w/api.php?action=query&format=json&titles={}".format(lang, title)

    #set session
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    #use session to retrive data
    #response =requests.get(api)
    response =session.get(api)
    responsedata = returnJsonCheck(response)
    page_id = list(responsedata["query"]["pages"].keys())[0]
    return page_id


def getLanglinks(title):
    """insert english article title, output language links zh, en, es, ar 
    as article_lang_links = {"ar": [title, pageid, url], "en": [], ...}"""
    
    api = "https://en.wikipedia.org/w/api.php?action=query&format=json&titles={}&prop=langlinks&lllimit=500&llprop=langname|url".format(title)
    
    #set session
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    #response =requests.get(api)
    response =session.get(api)
    responsedata = returnJsonCheck(response)
    page_id = list(responsedata["query"]["pages"].keys())[0]
    alllanglst=responsedata['query']['pages'][page_id].get('langlinks')
    
    article_lang_links = {'ar':None, 'zh':None, 'es':None}
    if alllanglst is not None:
        for langitem in alllanglst:
            if langitem['lang'] == 'ar':#['ar', 'zh', 'es']:
                ar_title = langitem['*']
                ar_url = langitem['url']
                #lang = langitem['lang']
                ar_pageid = getPageId('ar', ar_title)
                #print (lang)
                article_lang_links['ar'] = [ar_title, ar_pageid, ar_url]
            elif langitem['lang'] == 'zh':
                zh_title = langitem['*']
                zh_url = langitem['url']
                #lang = langitem['lang']
                zh_pageid = getPageId('zh', zh_title)
                #print (lang)
                article_lang_links['zh'] = [zh_title, zh_pageid, zh_url]
            elif langitem['lang'] == 'es':
                es_title = langitem['*']
                es_url = langitem['url']
                #lang = langitem['lang']
                es_pageid = getPageId('es', es_title)
                #print (lang)
                article_lang_links['es'] = [es_title, es_pageid, es_url]
    
    return (page_id, article_lang_links)    
    




if __name__ == "__main__":
    data = pd.read_table("/Users/angli/ANG/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/posted_itn_filter_death.csv", 
                                 sep=',', error_bad_lines = False)
    data = pd.read_table("/Users/jiajunluo/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/posted_itn_filter_death.csv", 
                                 sep=',', error_bad_lines = False)
    
    #collect the langlinks for all the articles
    #format as [postid, post_year, post_date, title, pageid, article_lang_links]
    all_article_langlinks = []
    i=0
    for index, row in data.iterrows():
        i+=1
        postid = str(int(row['postid']))
        post_year = str(int(row['year']))
        post_date = row['time']
        #article
        title = row['article']
        pageid, article_lang_links = getLanglinks(title)
        article_lang_links['en'] = [title, pageid]
        all_article_langlinks.append([postid, post_year, post_date, title, pageid, article_lang_links])
        if i%10==0: print (title)
    
    f = open('/Users/jiajunluo/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/all_article_langlinks.pkl', 'wb')   # Pickle file is newly created where foo1.py is
    pickle.dump(all_article_langlinks, f)          # dump data to f
    f.close() 

    f = open('/Users/jiajunluo/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/all_article_langlinks.pkl', 'rb')   # 'r' for reading; can be omitted
    mydict = pickle.load(f)         # load file content as mydict
    f.close()

    
    
    
    
    
    
    
    
    