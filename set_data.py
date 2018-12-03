#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  3 16:13:02 2018

this is to set data, merging different sources

@author: angli
"""

import pandas as pd
from collections import Counter

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
    alltopics = list(set(list(piddata['topic'])))
    topics = [x for x in alltopics if x != -1]
    if len(topics)==0:
        post_topic_dict[post_id] = -1
    else:
        c = Counter(topics)
        counts = c.most_common()
        if len(counts) == 1: 
            mostcommon_topic,  mostcommon_topic_counts = counts[0] 
            post_topic_dict[post_id] = mostcommon_topic
        else:
            mostcommon_topic,  mostcommon_topic_counts = counts[0]
            secondcommon_topic,  secondcommon_topic_counts = counts[1]
            if mostcommon_topic_counts != secondcommon_topic_counts:
                post_topic_dict[post_id] = mostcommon_topic
            else:
                post_topic_dict[post_id] = topics[0]