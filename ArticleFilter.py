"""
Created on Tue Mar  6 12:48:17 2018

@author: Keyang
"""

import requests
import re
import csv
import sys 

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
    if gapcontinue == "end":
        return ("end", [])
    requests_url = "https://zh.wikipedia.org/w/api.php?action=query&format=json&generator=allpages&gaplimit=500\
    &gapfilterredir=nonredirects&gapfilterlanglinks=withlanglinks&prop=langlinkscount&formatversion=2"
    requests_url = requests_url + "&gapcontinue="+gapcontinue if gapcontinue != None else requests_url
    r = requests.get(requests_url)
    result = returnJsonCheck(r)
    gapcontinue = result["continue"]["gapcontinue"] if "continue" in result else "end"
    pages = result["query"]["pages"]
    filtered_list = []
    for page in pages:
        pre_check = langlinkscountCheck(page["langlinkscount"])
        if pre_check:
            filtered_list.append(page)
    return (gapcontinue, filtered_list)

def getWikiITNPages(gcontinue = None):
    if gcontinue == "end":
        return ("end", [])
    requests_url = "https://en.wikipedia.org/w/api.php?action=query&format=json&formatversion=2&prop=revisions&generator=embeddedin&geititle=Template:ITN%20candidate&rvprop=timestamp%7Cuser%7Ccomment%7Ccontent&geilimit=10"
    requests_url = requests_url + "&geicontinue="+gcontinue if gcontinue != None else requests_url
    r = requests.get(requests_url)
    result = returnJsonCheck(r)
    gcontinue = result["continue"]["geicontinue"] if "continue" in result else "end"
    pages = result["query"]["pages"]
    filtered_list = []
    for page in pages:
        if "Wikipedia:In the news/Candidates/" in page['title']:
            print(page['title'])
            filtered_list.append(page)
    return (gcontinue, filtered_list)    

# return True if both en and es existed in the langlinks list
def checkMultiLang(lang_link_list: list) -> bool:
    lang_list = ['en', 'es']
    counter = 0
    langs = {}
    for lang in lang_link_list:
        if lang['lang'] in lang_list:
            counter += 1
            langs[lang['lang']] = lang['*']
    
    if counter == 2:
        return multiLangCreationTime(langs['en'], 'en') and multiLangCreationTime(langs['es'], 'es')
    else:
        return False

# return True if the creation time falls between a pre-defined range
# creation time equals to the first revision time
def checkCreationTime(creation_time: str) -> bool:
    return True if creation_time > "2016-01-01T00:00:00Z" else False

def multiLangCreationTime(title: str, language: str) -> bool:
    request_url = "https://en.wikipedia.org/w/api.php?action=query&format=json&prop=revisions&rvlimit=1&formatversion=2&rvprop=timestamp&rvdir=newer&titles="\
    + title if language == "en" else \
    "https://es.wikipedia.org/w/api.php?action=query&format=json&prop=revisions&rvlimit=1&rvprop=timestamp&rvdir=newer&formatversion=2&titles=" + title
    
    # print(request_url)
    r_creation_time = requests.get(request_url)
    
    if apiErrorCheck(r_creation_time.headers)[0]:
        print("ERROR", title, apiErrorCheck(r_creation_time.headers)[1])
        return False
    
    r_json = returnJsonCheck(r_creation_time)
    if 'revisions' not in r_json['query']['pages'][0]:
        print(" ERROR ")
        print(r_json)
        print(" ")
        return False
    return checkCreationTime(r_json['query']['pages'][0]['revisions'][0]['timestamp'])

def apiErrorCheck(headers: dict):
    if "MediaWiki-API-Error" in headers:
        return (True, headers['MediaWiki-API-Error'])
    else:
        return (False, "no errors")

def returnJsonCheck(response) -> dict:
    try:
        return response.json()
    except:
        print("ERROR")
        print(response)
        sys.exit("json error")
    
# check if a page fits our defined params => 
#   * having zh, en, es language page 
#   * is created in a pre-defined timespan
def checkPageParams(id) -> bool:
    request_url = "https://zh.wikipedia.org/w/api.php?action=query&format=json&prop=revisions|langlinks&rvlimit=1\
    &rvprop=timestamp&rvdir=newer&lllimit=50&pageids=" + id

    r_params = requests.get(request_url)

    if apiErrorCheck(r_params.headers)[0]:
        print("ERROR", id, apiErrorCheck(r_params.headers)[1])
        return False

    r_params = returnJsonCheck(r_params)
    multi_lang_list = r_params['query']['pages'][id]['langlinks']
    time_stamp = r_params['query']['pages'][id]['revisions'][0]['timestamp']
    check_result = checkCreationTime(time_stamp) and checkMultiLang(multi_lang_list)

    return check_result

def decipherWikiITNPage(content: str) -> list:
    itn_lists = []
    content_by_days = re.split(r'(==\W?\w+? \d{1,2}\W?==)', content)
    if len(content_by_days) <= 1:
        print("fail to split based on day")
        # print(content_by_days)
        return itn_lists
    
    itn_time = ""
    for bolb_day in content_by_days:    
        if re.match(r'(==\W?\w+? \d{1,2}\W?==)', bolb_day):
            itn_time = bolb_day.strip().split("==")[1].strip()
            continue
        itn_candidates = re.split(r'(\n====.+====\n)', bolb_day)[1:]
        itn_title = ""
        for itn_candidate in itn_candidates:
            if re.match(r'(\n====.+====\n)', itn_candidate):
                print(itn_candidate)
                itn_title = itn_candidate.strip().split("====")[1]
                continue
            itn_msg = ""
            for itn_split in re.split(r'(\{\{ITN candidate[\s\S]+?\}\}\n)', itn_candidate):
                # print(itn_split)
                if re.match(r'(\{\{ITN candidate[\s\S]+?\}\}\n)', itn_split):
                    itn_msg = itn_split
                    break
            itn = decipherITNTemplate(itn_time, itn_title, itn_msg)
            itn_lists.append(itn)
    return itn_lists  

def decipherITNTemplate(time: str, title: str, content: str) -> dict:
    result = {"time":time, "header":title, "article": "", "article2": "", "image": "", "blurb": "", "recent deaths": "", "ongoing": "", "altblurb": "", 
    "altblurb2": "", "altblurb3": "", "altblurb4": "", "sources": "", "updated": "", "updated2": "", "nominator": "", 
    "updater": "", "updater2": "", "updater3": "", "ITNR": "", "nom cmt": "", "sign": ""}
    
    itn_params = content.strip().split("| ")[1:]
    for param in itn_params:
        print(param)
        temp = re.split(r'\W=\W', param)
        key = temp[0].strip()
        value = ""
        if len(temp) >= 2:
            value = temp[1].strip() if not re.match(r'<--.+-->', temp[1].strip()) else ""
            value = temp[1].strip()
        
        if key == "sign":
            value = value.split("(UTC)")[0] + "(UTC)"

        value = value.replace("\n", " ")
        if key in result.keys():
            result[key] = value

    return result


def writeRowsCSV(rows: list, fieldnames = ["pageid", "title"]):
    with open('itns.csv', 'a') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames = fieldnames)
        # writer.writeheader()
        for row in rows:
            writer.writerow(row)

def collectingArticles(gapcontinue = None):
    while gapcontinue != "end":
        print(gapcontinue)
        gapcontinue, pages = getWikiPages(gapcontinue)
        filtered_pages = []
        for page in pages:
            if checkPageParams(str(page["pageid"])):
                page.pop('ns', None)
                page.pop('langlinkscount', None)
                filtered_pages.append(page)
                print(" ", page['title'])
        
        if len(filtered_pages) > 0:
            writeRowsCSV(filtered_pages)
    

def collectingITNEntries(gcontinue = None):
    field_names = ["year", "time", "header", "article", "article2", "image", "blurb", "recent deaths", "ongoing", "altblurb", 
        "altblurb2", "altblurb3", "altblurb4", "sources", "updated", "updated2", "nominator", 
        "updater", "updater2", "updater3", "ITNR", "nom cmt", "sign"]
    while gcontinue != "end":
        print(gcontinue)
        gcontinue, itn_pages = getWikiITNPages(gcontinue)
        itns = []
        for itn_page in itn_pages:
            # print(itn_page)
            itns = decipherWikiITNPage(itn_page['revisions'][0]['content'])
            year = itn_page['title'].strip()[-4:]
            itns = [(lambda itn: dict(itn.items() | {'year':year}.items()))(itn) for itn in itns] # adding year data into the result

            if len(itns) > 0:
                writeRowsCSV(itns, field_names)

collectingITNEntries(None)

