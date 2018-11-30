#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 09:36:50 2018

this is to write out from langlinks pickle

@author: angli
"""
import pickle


if __name__ == "__main__":
    
    #read pickle
    f = open('/Users/angli/ANG/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/all_article_langlinks.pkl', 'rb')   # 'r' for reading; can be omitted
    article_langlinks = pickle.load(f)         # load file content as mydict
    f.close()
    
    #write out
    f = open("/Users/angli/ANG/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/post_articles_set_r1.csv", "w")
    #write first row
    f.write('"postid","postyear","postdate","en_title","en_pageid","ar","ar_pageid","ar_title","zh","zh_pageid","zh_title","es","es_pageid","es_title"\n')
    
    
    for item in article_langlinks:
        postid = '"{}"'.format(str(item[0]))
        postyear = '"{}"'.format(str(item[1]))
        postdate = '"{}"'.format(str(item[2]))
        en_title = '"{}"'.format(str(item[3]))
        en_pageid = '"{}"'.format(str(item[4]))
        
        #this is the pagelang dict
        article_langs = item[5]
        #check langlinks
        #for ar, ar_pageid, ar_title, zh, zh_pageid, zh_title, es, es_pageid, es_title
        lang_pageinfo = [postid, postyear, postdate, en_title, en_pageid, '"False"', '""', '""', '"False"', '""', '""', '"False"', '""', '""'] 
        if article_langs["ar"] is not None: 
            lang_pageinfo[5] = '"{}"'.format("True")
            lang_pageinfo[6] = '"{}"'.format(str(article_langs["ar"][1]))
            lang_pageinfo[7] = '"{}"'.format(str(article_langs["ar"][0]))
        if article_langs["zh"] is not None: 
            lang_pageinfo[8] = '"{}"'.format("True")
            lang_pageinfo[9] = '"{}"'.format(str(article_langs["zh"][1]))
            lang_pageinfo[10] = '"{}"'.format(str(article_langs["zh"][0]))
        if article_langs["es"] is not None: 
            lang_pageinfo[11] = '"{}"'.format("True")
            lang_pageinfo[12] = '"{}"'.format(str(article_langs["es"][1]))
            lang_pageinfo[13] = '"{}"'.format(str(article_langs["es"][0]))
        
        #only write out with at least 1 other lang links
        if lang_pageinfo[5] == '"True"' or lang_pageinfo[8]== '"True"' or lang_pageinfo[11]== '"True"':
            line_string = ",".join(lang_pageinfo)+"\n"
            f.write(line_string)
        
    f.close()
        
    