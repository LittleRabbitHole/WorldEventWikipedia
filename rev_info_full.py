 # By Zhou Yingfan, Keyang

import pandas as pd
import re
# from bs4 import BeautifulSoup
import requests
import json
#import csv

#import rev_quality as rq

# get the page data
def getPageInfo(revid,article_id,language):
    content=""
    url='https://'+language+'.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=ids|timestamp|size|content&format=json&inprop=url&revids='+str(revid)
    web_data = requests.get(url)
    datas = json.loads(web_data.text)
    content=datas["query"]["pages"][str(article_id)]["revisions"][0].get("*")
    size = datas["query"]["pages"][str(article_id)]["revisions"][0].get("size")
    timestamp = datas["query"]["pages"][str(article_id)]["revisions"][0].get("timestamp")
    return (content, size,timestamp)

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

def sectionNoList(content):
    pattern = re.compile(r'\=\=.*\=\=.*\n')
    result=pattern.findall(content)
    sectionNoList=[]
    for section in result:
        sectionNoList.append(section.count('='))
    return sectionNoList


def qualityMeasures(revid, article_id, lang):
    content, size, timestamp = getPageInfo(revid, article_id, lang)
    measures = {}
    if content:
        measures['timestamp'] = timestamp
        measures['size'] = size
        measures['references'] = refNum(content)
        measures['wiki_links'] = wikiNum(content)
        measures['external_links'] = exNum(content)

        #sectionNoList=[]
        pattern = re.compile(r'\=\=.*\=\=.*\n')
        result_sec=pattern.findall(content)
        sectionNoList=[]
        # change section list into number list
        for section in result_sec:
            sectionNoList.append(section.count('='))
        if sectionNoList:
            measures['section_depth']=len(set(sectionNoList))
            measures['section_breadth']=sectionNoList.count(4)
            measures['section_num']=len(sectionNoList)
        else:
            measures['section_depth']=0
            measures['section_breadth']=0
            measures['section_num']=0
    else:
        measures['timestamp'] = -1
        measures['size'] = -1
        measures['references'] = -1
        measures['wiki_links'] = -1
        measures['external_links'] = -1
        measures['section_depth']=-1
        measures['section_breadth']=-1
        measures['section_num']=-1
    
    return measures


if __name__ == "__main__":
    linkInfo = pd.read_csv("data/rev_pool_candidate.csv")
    # cnLinkInfo=linkInfo[linkInfo.language=='es']
    result = []
    langs = {'en': 'en', 'es': 'es', 'cn': 'zh'}
     
    for idx,row in linkInfo.iterrows():
        entry = row.to_dict()
        revid = row['revid']
        print(revid)
        language = row['language']
        article_id = row['article_id']
    
        content = getPageInfo(revid, article_id, langs[language])
    
        if content:
            entry['references'] = refNum(content)
            entry['wiki_links'] = wikiNum(content)
            entry['external_links'] = exNum(content)
    
            #sectionNoList=[]
            pattern = re.compile(r'\=\=.*\=\=.*\n')
            result_sec=pattern.findall(content)
            sectionNoList=[]
            # change section list into number list
            for section in result_sec:
                sectionNoList.append(section.count('='))
            if sectionNoList:
                entry['section_depth']=len(set(sectionNoList))
                entry['section_breadth']=sectionNoList.count(4)
                entry['section_num']=len(sectionNoList)
            else:
                entry['section_depth']=0
                entry['section_breadth']=0
                entry['section_num']=0
        else:
            entry['references'] = -1
            entry['wiki_links'] = -1
            entry['external_links'] = -1
            entry['section_depth']=-1
            entry['section_breadth']=-1
            entry['section_num']=-1
        
        # sectionNoList=[]
        # pattern = re.compile(r'\=\=.*\=\=.*\n')
        # result=pattern.findall(content)
        # sectionNoList=[]
        # # change section list into number list
        # for section in result:
        #     sectionNoList.append(section.count('='))
        # if sectionNoList:
        #     sectionDepth=len(set(sectionNoList))
        #     sectionBreadth=sectionNoList.count(4)
        #     sectionNo=len(sectionNoList)
        
        result.append(entry)
    
    df_full = pd.DataFrame(result)
    df_full.to_csv('data/rev_candidate_full.csv')


# for value in cnLinkInfo.iterrows():
#     revid=value[1]['revid']
#     language=value[1]['language']
#     article_id=value[1]['article_id']
    
#     list1=[]
#     ref=0
#     wiki=0
#     ex=0
#     # sectionDepth=0
#     # sectionBreadth=0
#     # sectionNo=0
    
#     content=getPageInfo(revid,article_id)
    
#     if content:
#         ref=refNum(content)
#         wiki=wikiNum(content)
#         ex=exNum(content)
#         sectionNoList=[]
#         pattern = re.compile(r'\=\=.*\=\=.*\n')
#         result=pattern.findall(content)
#         # sectionNoList=[]
#         #change section list into number list
#         # for section in result:
#         #     sectionNoList.append(section.count('='))
#         # if sectionNoList:
#         #     sectionDepth=max(sectionNoList)/2
#         #     sectionBreadth=sectionNoList.count(4)
#         #     sectionNo=len(sectionNoList)
#     list1=[revid,language,article_id,ref,wiki,ex]
#     with open("result_es.csv", "a+",newline="",encoding='utf-8-sig') as f:
#         writer = csv.writer(f)
#         writer.writerow(list1)
#     f.close()