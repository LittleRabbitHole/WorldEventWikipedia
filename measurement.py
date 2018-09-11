import pandas as pd
import re
# from bs4 import BeautifulSoup
import requests
import json
import csv

#get the page data
def getPageInfo(revid,article_id,language):
    content=""
    url='https://' + language + '.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&format=json&inprop=url&revids='+str(revid)
    web_data = requests.get(url)
    datas = json.loads(web_data.text)
    if("*" in datas["query"]["pages"][str(article_id)]["revisions"][0].keys() ):
        content=datas["query"]["pages"][str(article_id)]["revisions"][0]["*"]
    return content

#get reference number
def refNum(content):
    refNum=content.count('</ref>')
    return refNum

#get wikiLink number
def wikiNum(content):
    pattern = re.compile(r'\[\[.*?]]')
    result=pattern.findall(content)
    wiki=len(result)
    return wiki

#get external link number
def exNum(content):
    #the external links which appear in the article
    pattern1 = re.compile(r'\[.*:\/\/.*?]')
    result_article=pattern1.findall(content)
    num_article=len(result_article)
    
    #the external links which appear after article
    pattern2 = re.compile(r'\*.*:\/\/.*')
    result_bottom=pattern2.findall(content)
    num_bottom=len(result_bottom)
    
    result=num_article+num_bottom
    return result

#change section list into number list
def sectionNoList(content):
    pattern = re.compile(r'\=\=.*\=\=.*\n')
    result=pattern.findall(content)
    sectionNoList=[]
    for section in result:
        sectionNoList.append(section.count('='))
    return sectionNoList

langs = {'en': 'en', 'es': 'es', 'cn': 'zh'}
df_rev_candidates = pd.read_csv('data/rev_pool_candidate.csv')

