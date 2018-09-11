# By Zhou Yingfan

import pandas as pd
import re
# from bs4 import BeautifulSoup
import requests
import json
import csv

# get the page data
def getPageInfo(revid,article_id,language):
    content=""
    url='https://'+language+'.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&format=json&inprop=url&revids='+str(revid)
    web_data = requests.get(url)
    datas = json.loads(web_data.text)
    if("*" in datas["query"]["pages"][str(article_id)]["revisions"][0].keys() ):
        content=datas["query"]["pages"][str(article_id)]["revisions"][0]["*"]
    return content

#get reference number
def refNum(content):
    refNum=content.count('<ref')
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


linkInfo = pd.read_csv("data/rev_pool_candidate.csv")
# cnLinkInfo=linkInfo[linkInfo.language=='es']
result = []

for idx,row in linkInfo.iterrows():
    entry = row.to_dict()


for value in cnLinkInfo.iterrows():
    revid=value[1]['revid']
    language=value[1]['language']
    article_id=value[1]['article_id']
    
    list1=[]
    ref=0
    wiki=0
    ex=0
    # sectionDepth=0
    # sectionBreadth=0
    # sectionNo=0
    
    content=getPageInfo(revid,article_id)
    
    if content:
        ref=refNum(content)
        wiki=wikiNum(content)
        ex=exNum(content)
        sectionNoList=[]
        pattern = re.compile(r'\=\=.*\=\=.*\n')
        result=pattern.findall(content)
        # sectionNoList=[]
        #change section list into number list
        # for section in result:
        #     sectionNoList.append(section.count('='))
        # if sectionNoList:
        #     sectionDepth=max(sectionNoList)/2
        #     sectionBreadth=sectionNoList.count(4)
        #     sectionNo=len(sectionNoList)
    list1=[revid,language,article_id,ref,wiki,ex]
    with open("result_es.csv", "a+",newline="",encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(list1)
    f.close()