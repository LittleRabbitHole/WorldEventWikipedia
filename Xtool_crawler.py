#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 13:40:35 2018

parser of Wikipedia Xtool
https://xtools.wmflabs.org/articleinfo

@author: Ang
"""

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.parse import quote
import pandas as pd
import pickle
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry



def session_request_soup(site):
    #set session
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    #use session to retrive data
    #site= "https://xtools.wmflabs.org/articleinfo/en.wikipedia.org/Black%20Lives%20Matter"
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
    
    req = session.get(site, headers=hdr) #{'User-Agent': 'Mozilla/5.0'}
    webpage = req.text
    soup = BeautifulSoup(webpage, features="lxml")
    return soup


def request_soup(site):
    #site= "https://xtools.wmflabs.org/articleinfo/en.wikipedia.org/Black%20Lives%20Matter"
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
    
    req = Request(site, headers=hdr) #{'User-Agent': 'Mozilla/5.0'}
    webpage = urlopen(req).read()
    soup = BeautifulSoup(webpage, features="xml")
    
    return soup


def monthly_edit(soup):
    #this is to return the monthly edit table
    monthly_table = soup.find_all("table", class_="table table-bordered table-hover table-striped month-counts-table")
    month = monthly_table[0].find_all('td', class_="sort-entry--month")
    edits = monthly_table[0].find_all('td', class_="sort-entry--edits")

    edit_lst = []
    month_lst = []
    
    for i in range(len(month)):
        month_lst.append(month[i].get_text().strip())
        edit_lst.append(edits[i].get_text().strip())

    monthly_df = pd.DataFrame({'month':month_lst, "edit":edit_lst})
    
    return monthly_df


def get_cleantext(findall_lst):
    clean_lst = []
    
    for i in range(len(findall_lst)):
        clean_lst.append(findall_lst[i].get_text().replace('\n', ' ').strip())
    
    return clean_lst
    


def general_stats(soup):
    #this is to return the general stats tabel
    general_section = soup.find(id="general-stats")
    all_tables = general_section.find_all("table")
    
    #parse into list
    all_tables_lst = []
    for table_raw in all_tables:
        table = table_raw.find_all('td')
        table_lst = get_cleantext(table)       
        all_tables_lst.append(table_lst)
    
    #convert into dict for convennient
    indx_lst = []
    stats_lst = []
    for table_lst in all_tables_lst:
        if len(table_lst)%2 == 0:
            indx = table_lst[::2]
            stats = table_lst[1::2]
        else:
            indx = table_lst[1::2]
            stats = table_lst[2::2]
        #add element
        indx_lst += indx
        stats_lst += stats

    #general_stats_df = pd.DataFrame({'idx':indx_lst, "stats":stats_lst})
    
    general_states = dict(zip(indx_lst, stats_lst))
    
    return general_states


def article_monthly_edits():
    #provide a list of articles, return montly edits for the articles
    f = open("/Users/ANG/OneDrive/Documents/Pitt_PhD/ResearchProjects/Wiki_Event/data/all133articles.txt")
    lines = f.readlines()
    f.close()
    
    all_df = pd.DataFrame({'month':[], "edit":[], "event":[], "title":[]})
    
    i = 0
    for line in lines:
        i += 1
        line_lst = line.strip().split("\t")
        title = line_lst[0]
        print (i, title)
        event = line_lst[1]
        site = "https://xtools.wmflabs.org/articleinfo/en.wikipedia.org/{}".format(title)
        soup = request_soup(site)
        table = monthly_edit(soup)
        table["event"] = event
        table["title"] = title
        all_df = all_df.append(table)
        
    #all_df.to_csv("total_monthly_edits.csv", index = False)
    return all_df


def articles_general_states():
    #input dataframe: ['postid', 'postyear', 'postdate', 'en_title', 'en_pageid',
       #'ar'(T/F),'ar_pageid', 'ar_title', 'zh'(T/F), 'zh_pageid', 'zh_title', 'es'(T/F), 'es_pageid', 'es_title']
    #return list of posts with gstates content
    
#    data = pd.read_table("/Users/angli/ANG/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/post_articles_set_r1.csv", 
#                         sep=',', error_bad_lines = False)
    
    data = pd.read_table("/Users/jiajunluo/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/post_articles_set_r1.csv", 
                         sep=',', error_bad_lines = False)
    
    safechar = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~\t\n\r\x0b\x0c'
    
    #this is for all 
    #allxtooldatalst is a dict of {...,(postid, postyear, postdate):articles_gstates,...} where articles_gstates as format of {en:{}, es:{}, cn:{}, ar:{}}
    allxtooldatalst = {} 
    
    #place holder for error_articles
    error_articles = {}
    
    for index, row in data.iterrows():
        if index % 10 == 0: print (index)
        
        #post metadata
        postid = str(row["postid"]) 
        postyear = str(row["postyear"])
        postdate = str(row["postdate"])
        post_key = (postid, postyear, postdate)
        #first mond
        posttime = postyear + 
        
        #for each post -- good
        allxtooldatalst[post_key] = None #(postid, postyear, postdate): {en:{}, es:{}, cn:{}, ar:{}
        
        #content from xtools
        articles_gstates = {}
        articles_gstates['en'] = None
        articles_gstates['zh'] = None
        articles_gstates['es'] = None
        articles_gstates['ar'] = None
        
        #english
        title = row["en_title"] 
        #pageid = row["en_pageid"] 
        en_site = "https://xtools.wmflabs.org/articleinfo/en.wikipedia.org/{}".format(title)#/2011-03-24/2011-04-24
        en_site = quote(en_site, safe = safechar) #encode #safe = string.printable
        try:
            en_soup = session_request_soup(en_site)
            en_stats = general_stats(en_soup)
            articles_gstates['en'] = en_stats
        except Exception as e: 
            print ("en", title)
            error_articles[title] = ['en', post_key, str(e)]
        
        #chinese
        if row['zh'] == True: 
            zh_title = row['zh_title']
            #zh_pageid = str(int(row["zh_pageid"]))
            zh_site = "https://xtools.wmflabs.org/articleinfo/zh.wikipedia.org/{}".format(zh_title)
            zh_site = quote(zh_site, safe = safechar) #encode
            try:
                zh_soup = session_request_soup(zh_site)
                zh_stats = general_stats(zh_soup)
                articles_gstates['zh'] = zh_stats
            except Exception as e:
                print ("zh", zh_title)
                error_articles[zh_title] = ['zh', post_key, str(e)]
        #esp    
        if row['es'] == True:
            es_title = row['es_title']
            #es_pageid = str(int(row["es_pageid"]))
            es_site = "https://xtools.wmflabs.org/articleinfo/es.wikipedia.org/{}".format(es_title)
            es_site = quote(es_site, safe = safechar) #encode
            try:
                es_soup = session_request_soup(es_site)
                es_stats = general_stats(es_soup)
                articles_gstates['es'] = es_stats
            except Exception as e:
                print ("es", es_title)
                error_articles[es_title] = ['es', post_key, str(e)]

        #arb    
        if row['ar'] == True:
            ar_title = row['ar_title']
            #ar_pageid = str(int(row["ar_pageid"]))
            ar_site = "https://xtools.wmflabs.org/articleinfo/ar.wikipedia.org/{}".format(ar_title)
            ar_site = quote(ar_site, safe = safechar) #encode
            try:
                ar_soup = session_request_soup(ar_site)
                ar_stats = general_stats(ar_soup)
                articles_gstates['ar'] = ar_stats
            except Exception as e:
                print ("ar", ar_title)
                error_articles[ar_title] = ['ar', post_key, str(e)]
            
        #add each general_states as content into all allxtooldatalst
        allxtooldatalst[post_key] = articles_gstates
    
    return [allxtooldatalst, error_articles]


def errorRecollection(error_articles, allxtooldatalst):
    #safechar = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~\t\n\r\x0b\x0c'
    
    for key, item in error_articles.items():
        title = key
        lang = item[0]
        postid = item[1]
        
        #site = "https://xtools.wmflabs.org/articleinfo/{}.wikipedia.org/{}".format(lang, title)
        #site = quote(site, safe = safechar) #encode #safe = string.printable
        site = "https://xtools.wmflabs.org/articleinfo/es.wikipedia.org/%C2%BFCu%C3%A1ndo%20te%20casas%3F"
        try:
            soup = session_request_soup(site)
            stats = general_stats(soup)
            allxtooldatalst[postid][lang] = stats
        except Exception as e: 
            print (lang, title)
        
    



if __name__ == "__main__":
    [allxtooldatalst, error_articles] = articles_general_states()
        
    pickle.dump( allxtooldatalst, open( "/Users/angli/ANG/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/post_article_xtools.p", "wb" ) )
    pickle.dump( error_articles, open( "/Users/angli/ANG/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/error_articles.p", "wb" ) )
    
    #read
    #articles_gstates = pickle.load( open( "/Users/ANG/OneDrive/Documents/Pitt_PhD/ResearchProjects/WikiWorldEvent/data/articles_gstates.p", "rb" ) )
    #error_articles = pickle.load( open( "/Users/ANG/OneDrive/Documents/Pitt_PhD/ResearchProjects/WikiWorldEvent/data/error_articles.p", "rb" ) )
