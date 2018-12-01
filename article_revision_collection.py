#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 23:09:23 2018

this is to collect the first month revision -- effort

@author: ang
"""

import pickle
import pandas as pd
import utilities
from datetime import datetime, timedelta
import numpy as np



def articleRevisions(data):
    
    #save as postid:{"en":[],"ar":[],"zh":[],"es":[]}
    article_revisions = {}
    #save as list of article revisiont
    article_revision_lst = []
    
    #iterate over posts to collect the article revisions for the first 1 month from the post date
    i=0
    for ind, row in data.iterrows():
        i+=1
        if i%10==0: print(i)
        
        postid = row["postid"]
        
        article_revisions[postid] = {"en":None,"ar":None,"zh":None,"es":None}
        
        postyear = str(row["postyear"])
        postdate = str(row["postdate"])
        postyeardate = str(row["postyear"])+"-"+str(row["postdate"])
        post_datetime = datetime.strptime(postyeardate,'%Y-%d-%b')
        postdatetime = datetime.strptime(postyeardate,'%Y-%d-%b').strftime("%Y-%m-%d")
        
        rvstart = post_datetime.strftime("%Y-%m-%dT00:00:00Z")
        post_datetime_1m = post_datetime + timedelta(days=+31)
        rvend = post_datetime_1m.strftime("%Y-%m-%dT00:00:00Z")
        en_pageid = str(int(row["en_pageid"])) if not pd.isna(row["en_pageid"]) else None
        ar_pageid = str(int(row["ar_pageid"])) if not pd.isna(row["ar_pageid"]) else None
        zh_pageid = str(int(row["zh_pageid"])) if not pd.isna(row["zh_pageid"]) else None
        es_pageid = str(int(row["es_pageid"])) if not pd.isna(row["es_pageid"]) else None
        
        if en_pageid is not None:
            en_article = [postid, "en", postyear, postdate, postdatetime, en_pageid]
            
            en_url = "https://en.wikipedia.org/w/api.php?action=query"\
            "&format=json&prop=revisions&rvdir=newer&rvstart={}&rvend={}"\
            "&rvprop=ids|timestamp|user|userid|size&pageids={}&rvlimit=500".format(rvstart, rvend, en_pageid)
            try:
                en_page_revis = utilities.GetPageRevision(en_url)
            except:
                en_page_revis = []
            
            en_article.append(en_page_revis)
            article_revisions[postid]["en"] = en_article
            article_revision_lst.append(en_article)
            
        if ar_pageid is not None:
            ar_article = [postid, "ar", postyear, postdate, postdatetime, ar_pageid]
            
            ar_url = "https://ar.wikipedia.org/w/api.php?action=query"\
            "&format=json&prop=revisions&rvdir=newer&rvstart={}&rvend={}"\
            "&rvprop=ids|timestamp|user|userid|size&pageids={}&rvlimit=500".format(rvstart, rvend, ar_pageid)
            try:
                ar_page_revis = utilities.GetPageRevision(ar_url)
            except:
                ar_page_revis = []
                
            ar_article.append(ar_page_revis)
            article_revisions[postid]["ar"] = ar_article
            article_revision_lst.append(ar_article)
                
        if zh_pageid is not None:
            zh_article = [postid, "zh", postyear, postdate, postdatetime, zh_pageid]
            
            zh_url = "https://zh.wikipedia.org/w/api.php?action=query"\
            "&format=json&prop=revisions&rvdir=newer&rvstart={}&rvend={}"\
            "&rvprop=ids|timestamp|user|userid|size&pageids={}&rvlimit=500".format(rvstart, rvend, zh_pageid)
            try:
                zh_page_revis = utilities.GetPageRevision(zh_url)
            except:
                zh_page_revis = []

            zh_article.append(zh_page_revis)
            article_revisions[postid]["zh"] = zh_article
            article_revision_lst.append(zh_article)
            
        if es_pageid is not None:
            es_article = [postid, "es", postyear, postdate, postdatetime, es_pageid]
            
            es_url = "https://es.wikipedia.org/w/api.php?action=query"\
            "&format=json&prop=revisions&rvdir=newer&rvstart={}&rvend={}"\
            "&rvprop=ids|timestamp|userid|size&pageids={}&rvlimit=500".format(rvstart, rvend, es_pageid)
            try: 
                es_page_revis = utilities.GetPageRevision(es_url)  
            except:
                es_page_revis = []

            es_article.append(es_page_revis)
            article_revisions[postid]["es"] = es_article
            article_revision_lst.append(es_article)
    
    #final return        
    return (article_revisions, article_revision_lst)


if __name__ == "__main__":
    f = open('/Users/jiajunluo/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/post_article_xtools.p', 'rb')   # 'r' for reading; can be omitted
    all_articles = pickle.load(f)         # load file content as mydict
    f.close()
    
    data = pd.read_table("/Users/jiajunluo/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/post_articles_set_r1.csv", 
                             sep=',', error_bad_lines = False)
    
    article_revisions, article_revision_lst = articleRevisions(data)
    
    len(article_revision_lst)#6730
    len(list(article_revisions.keys()))#2064
    
    pickle.dump( article_revision_lst, open( "/Users/jiajunluo/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/article_revisions_list_6739.p", "wb" ) )
    pickle.dump( article_revisions, open( "/Users/jiajunluo/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/article_revisions_dict_2064.p", "wb" ) )


#"2011-04-09T13:27:29Z"
#url = '''https://en.wikipedia.org/w/api.php?action=query&format=json&prop=revisions
#    &rvdir=newer&rvstart={}&rvend={}&rvprop=ids|timestamp|user|userid|commen|size
#    &pageids={}&rvlimit=500'''.format(rvstart, rvend, pageid)
#
#
#f = open('/Users/angli/ANG/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/post_article_xtools.p', 'rb') 
#all_articles = pickle.load(f)         # load file content as mydict
#f.close()

