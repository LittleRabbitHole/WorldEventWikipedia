#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 23:09:23 2018

@author: jiajunluo
"""

import pickle
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.parse import quote
import pandas as pd
import lxml

f = open('/Users/jiajunluo/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/error_articles.p', 'rb')   # 'r' for reading; can be omitted
error_articles = pickle.load(f)         # load file content as mydict
f.close()

f = open('/Users/jiajunluo/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/post_article_xtools.p', 'rb')   # 'r' for reading; can be omitted
all_articles = pickle.load(f)         # load file content as mydict
f.close()


list(error_articles.keys())[0]

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
    soup = BeautifulSoup(webpage, features="lxml")#features="lxml"
    
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

safechar = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~\t\n\r\x0b\x0c'

title =  list(error_articles.keys())[1] #error in the title "285263) 1998 QE2"
en_site = "https://xtools.wmflabs.org/articleinfo/en.wikipedia.org/{}".format(title)
en_site = quote(en_site, safe = safechar) #encode #safe = string.printable
try:
    en_soup = request_soup(en_site)
    en_stats = general_stats(en_soup)
    articles_gstates['en'][title] = en_stats
except Exception as e: 
    error_articles[title] = ['en', str(e)]
    
print(en_stats['First edit'])