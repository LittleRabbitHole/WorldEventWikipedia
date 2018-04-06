#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 12:48:17 2018

@author: Ang
"""

import pandas as pd
import os
import datetime
import numpy as np
import urllib.parse
import json
import csv
import os
import urllib
import pickle
import itertools



#API = "https://en.wikipedia.org/w/api.php?action=query&format=json&prop=links&plnamespace=0&pllimit=500&titles="
#pageTitle = "Portal:Current_events/March_2017"

if __name__ == "__main__":
    f = open("all133articles.txt")
    articles = f.readlines()
    f.close()

    f_ch = open("articles_ch.csv", "w", encoding="UTF-8")
    f_span = open("articles_span.csv", "w", encoding="UTF-8")
    
    csv_ch_f = csv.writer(f_ch)
    csv_span_f = csv.writer(f_span)
    #write first row
    csv_ch_f.writerow(['title', 'lang-ch', 'lang-span'])
    csv_span_f.writerow(['title', 'lang-span'])
    
    n=0
    for line in articles:
        n+=1
        line = line.strip()
        splitline = line.split("\t")
        title = splitline[0]
        event = splitline[1]
        url = "https://en.wikipedia.org/w/api.php?action=query&format=json&prop=langlinks&llprop=langname&lllimit=500&titles=" + title
        response=urllib.request.urlopen(url)
        str_response=response.read().decode('utf-8')
        responsedata = json.loads(str_response)
        page_id = list(responsedata["query"]["pages"].keys())[0]
        try:
            lang_data_lst=responsedata['query']['pages'][page_id]['langlinks']
            lang_list = list()
            for item in lang_data_lst:
                lang_list.append(item['langname'])
            
            if "Chinese" in lang_list: 
                csv_ch_f.writerow([title, event, "chinese", ""])
            else:
                csv_ch_f.writerow([title, event,  "no chinese"])
                
            if "Spanish" in lang_list: 
                csv_span_f.writerow([title, event, "spanish", ""])
            else:
                csv_span_f.writerow([title, event, "no spanish"])
                
        except KeyError:  
            csv_ch_f.writerow([title, event, "no other lang"])
            csv_span_f.writerow([title, event, "no other lang"])
    
    f_ch.close()
    f_span.close()