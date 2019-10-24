#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 14:35:29 2019

@author: jiajunluo
"""

import pandas as pd
import re
# from bs4 import BeautifulSoup
import requests
import json
#import csv


def getPageInfo(talkid,lang):
    url='https://'+lang+'.wikipedia.org/w/api.php?action=query&prop=templates&tllimit=500&format=json&pageids='+str(talkid)
    web_data = requests.get(url)
    datas = json.loads(web_data.text)
    try:
        allposibilities = datas['query']['pages'][talkid]['templates']
        templates = [x['title'] for x in allposibilities if x['ns'] == 10]
        translat_lst = ['مترجمة','traducido','translat']
        translatetemps = []
        for x in templates:
            res = [ele for ele in translat_lst if (ele in x.lower())]
            translatetemps += res
        if len(translatetemps)>0:
            return (1)
        else:
            return (0)
    except KeyError:
        return (-1) #no template


def getTalkID(lang, pageid):
    #url = https://en.wikipedia.org/w/api.php?action=query&prop=info&inprop=talkid&pageids=31142430
    url='https://'+lang+'.wikipedia.org/w/api.php?action=query&prop=info&inprop=talkid&format=json&pageids='+str(pageid)
    web_data = requests.get(url)
    datas = json.loads(web_data.text)
    try:
        talkid = datas['query']['pages'][pageid]['talkid']
        return (str(talkid))
    except KeyError:
        return (-1)


if __name__ == "__main__":
    linkInfo = pd.read_csv("/Users/jiajunluo/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/effort_dataset_r1.csv")
    
    #write out
    f = open("/Users/jiajunluo/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/translation_check.csv", "w")
    #write first row, column names
    f.write('postid,lang,postyear,postdatetime,pageid,talkid,translated\n')
    
    i=0
    for ind, row in linkInfo.iterrows():
        i+=1
        if i%50 == 0: print (i)
        
        #post info
        postid, lang, postyear, postdatetime, pageid = str(row['postid']), row['lang'], str(row['postyear']), row['postdatetime'], str(row['pageid'])
        talkid = getTalkID(lang, pageid)
        if talkid != -1:
            translated = getPageInfo(talkid,lang)
        else:
            translated = -2 #no talkpage
            
        #set together
        line = [postid, lang, postyear, postdatetime, pageid, talkid, translated] 
        line_str = [str(x) for x in line]
        
        #writeout
        line_string = ",".join(line_str)+"\n"
        f.write(line_string)
        
    f.close()
        

