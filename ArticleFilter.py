"""
Created on Tue Mar  6 12:48:17 2018

@author: Keyang
"""

import requests
import re
import csv

# request address for getting all pages from wikipedia
# Host: zh.wikipedia.org
# method: GET
# URL: /w/api.php
# params: action=query&format=json&generator=allpages&gaplimit=500
#           &gapfilterredir=nonredirects&gapfilterlanglinks=withlanglinks&prop=langlinkscount

# request for checking the page creation time (first revision)
# Host: zh.wikipedia.org
# method: GET
# URL: /w/api.php
# params: action=query&prop=revisions&rvlimit=1&rvprop=timestamp&rvdir=newer&pageids= 

# request for checking the page's multi-language links
# Host: zh.wikipedia.org
# method: GET
# URL: /w/api.php
# params: action=query&prop=langlinks&pageids= 

# return True if langlinks cout has at least 2
# serve as the initial screening for multi-language pages
def langlinkscountCheck(count: int) -> bool:
    return True if count >= 2 else False

def getWikiPages(gapcontinue=None):
    requests_url = "https://zh.wikipedia.org/w/api.php?action=query&format=json&generator=allpages&gaplimit=500\
    &gapfilterredir=nonredirects&gapfilterlanglinks=withlanglinks&prop=langlinkscount&formatversion=2"
    requests_url = requests_url + "&gapcontinue="+gapcontinue if gapcontinue != None else requests
    r = requests.get(requests_url)
    result = r.json()
    gapcontinue = result["continue"]["gapcontinue"] if "continue" in result else "end"
    pages = result["query"]["pages"]
    filtered_list = []
    for page in pages:
        pre_check = langlinkscountCheck(page["langlinkscount"])
        if pre_check:
            filtered_list.append(page)
    return (gapcontinue, filtered_list)

# return True if both en and es existed in the langlinks list
def checkMultiLang(lang_link_list: list) -> bool:
    lang_list = ['en', 'es']
    counter = 0
    for lang in lang_link_list:
        if lang['lang'] in lang_list:
            counter += 1
    
    return True if counter >= 2 else False

# return True if the creation time falls between a pre-defined range
# creation time equals to the first revision time
def checkCreationTime(creation_time: str) -> bool:
    return True if creation_time > "2016-01-01T00:00:00Z" else False

def apiErrorCheck(headers: dict):
    if "MediaWiki-API-Error" in headers:
        return (True, headers['MediaWiki-API-Error'])
    else:
        return (False, "no errors")
    
# check if a page fits our defined params => 
#   * having zh, en, es language page 
#   * is created in a pre-defined timespan
def checkPageParams(id) -> bool:
    request_url = "https://zh.wikipedia.org/w/api.php?action=query&format=json&prop=revisions|langlinks&rvlimit=1\
    &rvprop=timestamp&rvdir=newer&lllimit=50&pageids=" + id

    r_params = requests.get(request_url)

    if apiErrorCheck(r_params.headers)[0]:
        print(id, apiErrorCheck(r_params.headers)[1])
        return False

    r_params = r_params.json()
    multi_lang_list = r_params['query']['pages'][id]['langlinks']
    time_stamp = r_params['query']['pages'][id]['revisions'][0]['timestamp']
    check_result = checkCreationTime(time_stamp) and checkMultiLang(multi_lang_list)

    return check_result

def writeRowsCSV(rows: list):
    with open('multi_lang_list.csv', 'a') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames = ["pageid", "title"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

def collectingArticles():
    gapcontinue = None
    while gapcontinue != "end":
        gapcontinue, pages = getWikiPages(gapcontinue)
        filtered_pages = []
        for page in pages:
            if checkPageParams(page["pageid"]):
                filtered_pages.append(page)
        
        if len(filtered_pages) > 0:
            writeRowsCSV(filtered_pages)
    
# print(checkPageParams(str(323064)))

