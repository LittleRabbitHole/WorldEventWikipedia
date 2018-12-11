#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  3 16:13:02 2018

this is to set data, merging different sources

Step1: adding topic 
input:
    from post_topics
output:
    post_articles_topic_r1.csv
    efforts_topic_r1.csv
    quality_topic_r1.csv

@author: angli
"""

import pandas as pd
from collections import Counter
import numpy as np


def topicMatching():
    post_topic = pd.read_csv("/Users/angli/ANG/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/post_topics.csv")
    post_grouped = post_topic.groupby(['post_id'])
    
    post_topic_dict = {}
    
    n=0
    for pidgroup in post_grouped:
        n+=1
        #if n==12: break
        post_id = pidgroup[0]
        
        #select on before and after
        piddata = pidgroup[1]#.groupby(['after_first_event_edit']) 
        category = list(set(list(piddata['category'])))[0]
        alltopics = list(set(list(piddata['topic'].dropna())))
        topics = [str(int(x)) for x in alltopics if x not in [-1, -1.0, "-1"]]
        if len(topics)==0:
            post_topic_dict[post_id] = ["-1",category]
        else:
            c = Counter(topics)
            counts = c.most_common()
            if len(counts) == 1: 
                mostcommon_topic,  mostcommon_topic_counts = counts[0] 
                post_topic_dict[post_id] = [mostcommon_topic,category]
            else:
                mostcommon_topic,  mostcommon_topic_counts = counts[0]
                secondcommon_topic,  secondcommon_topic_counts = counts[1]
                if mostcommon_topic_counts != secondcommon_topic_counts:
                    post_topic_dict[post_id] = [mostcommon_topic,category]
                else:
                    post_topic_dict[post_id] = [topics[0],category]
    return  post_topic_dict          


def topicMatching2():
    post_topic = pd.read_csv("/Users/jiajunluo/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/post_articles_topic_r1.csv")
    post_grouped = post_topic.groupby(['postid'])
    
    post_topic_dict = {}
    
    n=0
    for pidgroup in post_grouped:
        n+=1
        #if n==12: break
        post_id = pidgroup[0]
        
        #select on before and after
        piddata = pidgroup[1]#.groupby(['after_first_event_edit']) 
        category = list(set(list(piddata['category'])))[0]
        topic = list(set(list(piddata['topic'].dropna())))[0]
        post_topic_dict[post_id] = [topic,category]
    return  post_topic_dict          


def addTopics(data, post_topic_dict):
    data["topic"] = ""
    data["category"] = ""
    for ind, row in data.iterrows():
        postid = row['postid']
        topic_cate = post_topic_dict.get(postid)
        if topic_cate is not None:
            topic = topic_cate[0]
            category = topic_cate[1]
            data.at[ind, "topic"] = topic
            data.at[ind, "category"] = category
        else:
            data.at[ind, "topic"] = ""
            data.at[ind, "category"] = ""
    return data        
        
    
                
if __name__ == "__main__":
    post_topic_dict = topicMatching()
    
    post_articles = pd.read_csv("/Users/angli/ANG/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/post_articles_set_r1.csv")
    post_articles_topic = addTopics(post_articles, post_topic_dict)
    post_articles_topic.to_csv('/Users/angli/ANG/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/post_articles_topic_r1.csv', index=False)
    
    #use updated topic
    post_topic_dict = topicMatching2()
    efforts = pd.read_csv("/Users/jiajunluo/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/effort_dataset_r1_v2.csv")
    efforts_topic = addTopics(efforts, post_topic_dict)
    efforts_topic.to_csv('/Users/jiajunluo/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/efforts_topic_r1_v2.csv', index=False)
    
    quality = pd.read_csv("/Users/angli/ANG/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/qualitymeasures_dataset_r1.csv")
    quality_topic = addTopics(quality, post_topic_dict)
    quality_topic.to_csv('/Users/angli/ANG/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/quality_topic_r1.csv', index=False)












































