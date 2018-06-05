"""
Created on Mon Jun  4 15:48:17 2018

@author: Keyang
"""

import requests
import re
import csv
import urllib
import sys
import ArticleFilter as utl

def getPageContent(title: str):
    r_url = "https://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles=" + urllib.parse.quote_plus(title) + "&rvprop=content&formatversion=2&format=json"
    r = requests.get(r_url)
    # print(r.h)
    result = utl.returnJsonCheck(r)
    # print(result)
    if "missing" in result['query']['pages'][0]:
        return ""
    content = redirectCheck(result['query']['pages'][0]['revisions'][0]['content'])

    return content

def getInfobox(title: str):
    content = getPageContent(title)
    if content is "":
        return (False, "missing|")
    # get the infobox type
    infobox_title = ""
    infobox_type = ""
    has_infobox = False
    for infobox_split in re.split(r'(Infobox .+?[\n\|])', content):
        # print(infobox_split)
        if re.match(r'(Infobox .+?[\n\|])', infobox_split):
            infobox_title = re.sub(r'\|', "", infobox_split)
            print(infobox_title.split(" ", 1)[1])
            has_infobox = True
            break
    if has_infobox:
        infobox_type = infobox_title.split(" ", 1)[1]

    return (has_infobox, infobox_type.strip())

def redirectCheck(content: str) -> str:
    if re.match(r'^#REDIRECT\W', content):
        print(" ", content)
        redirected_content = re.split(r'^#REDIRECT', content)[1]
        redirected_title = ""
        for redirected_content_split in re.split(r'(\[\[.+?\]\])', redirected_content):
            if re.match(r'(\[\[.+?\]\])', redirected_content_split):
                redirected_title = re.sub(r'[\[\]]', "", redirected_content_split)
                break
        # redirected_title = re.sub(r'[\[\]]', "", redirected_title)
        if redirected_title == "":
            print("#REDIRECT ERROR")
            print(" ", content)
            sys.exit("Can't find redirected destination")
        print(" ", redirected_title)
        return getPageContent(redirected_title)
    else:
        return content


def loadDataSet(file_name: str, position=None):
    data_set = []
    if position is None: 
        after_position = True
    else:
        after_position = False
    with open(file_name) as csv_file:
        reader = csv.DictReader(csv_file)
        print(type(reader))
        for row in reader:
            if row['header'] == position:
                after_position = True
            if not after_position:
                continue
            data_set.append({'year':row['year'], 'time':row['time'], 'header':row['header'], 'article':row['article'], 'article2':row['article2']})
    return data_set
