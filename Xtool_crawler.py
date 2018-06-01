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
    #input dataframe: 'year', 'time', 'article', 'zh'(T/F), 'es'(T/F), 'zh_title', 'es_title'
    #return dict as: article:[language, general_states]
    
    data = pd.read_table("/Users/ANG/OneDrive/Documents/Pitt_PhD/ResearchProjects/WikiWorldEvent/data/posted_itn.csv", 
                         sep=',', error_bad_lines = False)
    #all_articles = list(data['article']) + list(data['zh_title']) + list(data['es_title'])
    #all_articles = list(set(all_articles)) #5564 totle articles
    
#    f = open("/Users/ANG/OneDrive/Documents/Pitt_PhD/ResearchProjects/WikiWorldEvent/data/posted_itn.csv")
#    lines = f.read().split("\n\n")
#    f.close()
    
    articles_gstates = {}
    articles_gstates['en'] = {}
    articles_gstates['zh'] = {}
    articles_gstates['es'] = {}
    error_articles = {}
    
    safechar = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~\t\n\r\x0b\x0c'
    
    for index, row in data.iterrows():
        if index % 50 == 0: print (index)
        #posted_time = str(row['time']) + ', '+ str(row['year']) 
        
        #english
        title = row["article"] #error in the title "285263) 1998 QE2"
        en_site = "https://xtools.wmflabs.org/articleinfo/en.wikipedia.org/{}".format(title)
        en_site = quote(en_site, safe = safechar) #encode #safe = string.printable
        try:
            en_soup = request_soup(en_site)
            en_stats = general_stats(en_soup)
            articles_gstates['en'][title] = en_stats
        except Exception as e: 
            error_articles[title] = ['en', str(e)]
        
        #chinese
        if row['zh'] == True: 
            zh_title = row['zh_title']
            zh_site = "https://xtools.wmflabs.org/articleinfo/zh.wikipedia.org/{}".format(zh_title)
            zh_site = quote(zh_site, safe = safechar) #encode
            try:
                zh_soup = request_soup(zh_site)
                zh_stats = general_stats(zh_soup)
                articles_gstates['zh'][zh_title] = zh_stats
            except Exception as e:
                error_articles[title] = ['zh', str(e)]
        #esp    
        if row['es'] == True:
            es_title = row['es_title']
            es_site = "https://xtools.wmflabs.org/articleinfo/es.wikipedia.org/{}".format(es_title)
            es_site = quote(es_site, safe = safechar) #encode
            try:
                es_soup = request_soup(es_site)
                es_stats = general_stats(es_soup)
                articles_gstates['es'][es_title] = es_stats
            except Exception as e:
                error_articles[title] = ['es', str(e)]
    
    return [articles_gstates, error_articles]

[articles_gstates, error_articles] = articles_general_states()

pickle.dump( articles_gstates, open( "/Users/ANG/OneDrive/Documents/Pitt_PhD/ResearchProjects/WikiWorldEvent/data/articles_gstates.p", "wb" ) )
pickle.dump( error_articles, open( "/Users/ANG/OneDrive/Documents/Pitt_PhD/ResearchProjects/WikiWorldEvent/data/error_articles.p", "wb" ) )

#read
#articles_gstates = pickle.load( open( "/Users/ANG/OneDrive/Documents/Pitt_PhD/ResearchProjects/WikiWorldEvent/data/articles_gstates.p", "rb" ) )
#error_articles = pickle.load( open( "/Users/ANG/OneDrive/Documents/Pitt_PhD/ResearchProjects/WikiWorldEvent/data/error_articles.p", "rb" ) )
