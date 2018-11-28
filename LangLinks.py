#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 17:02:50 2018
Language link collection for a data frame with article title in English Wikipedia
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
import requests
import sys


def returnJsonCheck(response) -> dict:
    try:
        return response.json()
    except:
        print("ERROR")
        print(response)
        print(response.text)
        sys.exit("json error")
        

def getLanglinks(title):
    api = "https://en.wikipedia.org/w/api.php?action=query&titles={}&prop=langlinks&lllimit=500&llprop=langname|url&format=json".format(title)
    response =requests.get(api)
    responsedata = returnJsonCheck(response)
    page_id = list(responsedata["query"]["pages"].keys())[0]
    alllanglst=responsedata['query']['pages'][page_id]['langlinks']
    for langitem in alllanglst:
        if langitem['lang'] in ['ar', 'zh', 'es']:
            title = langitem['*']
            url = langitem['url']
            lang = langitem['lang']
        
    



data = pd.read_table("/Users/angli/ANG/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/posted_itn_filter.csv", 
                             sep=',', error_bad_lines = False)

for index, row in data.iterrows():
    title = row['article']
    