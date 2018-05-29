#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 29 14:10:22 2018

Sample code of how to collect the revision quality using  https://ores.wikimedia.org/v3

Revert revisions:  mwapi, mwreverts.api
Install: https://github.com/mediawiki-utilities/python-mwreverts
documentation on the mwrevert.api: https://github.com/mediawiki-utilities/python-mwreverts/blob/master/ipython/basic_usage.ipynb 


sample paper:
https://dl.acm.org/citation.cfm?id=2038585

@author: angli
"""

import pandas as pd
import os
import datetime
import numpy as np
import urllib.parse
import json
import csv
import urllib
import pickle
from Wiki_datacollections_all import GetUserContri

#read all the user ids
os.chdir("~/data")
fo = open("userids.txt")
lines=fo.readlines()
fo.close()

##########################################
#step1: collection of editor contribution
###i.e. contribution collections of 4 months data ####
##########################################

f = open("newcomer_article_contri_fourmonths.csv", "w", encoding="UTF-8")
csv_f = csv.writer(f)
#write first row
csv_f.writerow(['user','userid', 'wpid', 'event', 'usertype',
                'timestamp', 'ns',  'title', 'pageid', 'revid','parentid', 
                'sizediff', 'minor'])

#write error
f_error=open("newcomer_edit_errors.csv", "w", encoding="UTF-8")
csv_error = csv.writer(f_error)

#collect the user contribution within a time range (starttime, endtime) based on his/her userid
n=0
for line in lines[1::]:
    n+=1
    #print (n, line)
    line = line.strip()
    info_lst = line.split('\t')
    #userinfo
    userid = info_lst[1]
    print (n, userid)
    event = info_lst[-1]
    #usertype
    usertype = info_lst[-2]
    #get name from names list
    user = info_lst[0]
    #onemonth time window
    starttime = info_lst[2]+"T00:00:00Z"
    endtime = info_lst[4]+"T11:59:59Z"
    #get the contribution
    usercontri = GetUserContri(userid, starttime, endtime)
    if usercontri == "erroruser":
        csv_error.writerow([user])
    else:
        usercontribsdata = usercontri
        for feature in usercontribsdata:
            csv_f.writerow([user, feature['userid'], feature['user'], event, usertype,
                            feature['timestamp'],feature['ns'],feature['title'],
                            feature['pageid'], feature['revid'], feature['parentid'],
                            feature.get('sizediff','')])    
    #if n%10==0:

f.close()

##########################################
#collecting article quality based on the good-faith score from ORES: https://www.mediawiki.org/wiki/ORES

#This api is to look at the quality at the article level based on wp10 model
#https://ores.wikimedia.org/v3/scores/enwiki?models=wp10&revids=712140761 

#This api is to look at the quality for each of the revision
#https://ores.wikimedia.org/v3/scores/enwiki?models=goodfaith&revids=636074156
#https://ores.wikimedia.org/v3/scores/enwiki?models=reverted&revids=712140761

#can also stack the revids in one url request
#https://ores.wikimedia.org/v3/scores/enwiki?models=goodfaith&revids=753383232|753383231|753383230|753383229|753383228
##########################################

#read the contribution file
data = pd.read_csv("newcomer_article_contri_fourmonths.csv", encoding = "ISO-8859-1")
data.columns.values

userid_list = list(data['userid'])
usertyepe_list = list(data['usertype'])
event_list = list(data['event'])
revid_list = list(data['revid'])

#you can also stack for 20 revids together to collect the quality like using the url like:
#https://ores.wikimedia.org/v3/scores/enwiki?models=goodfaith&revids=753383232|753383231|753383230|753383229|753383228
revid_stack_list = []
n=0
revid_stack = ""
for revid in revid_list: 
    n+=1
    revid = str(revid)
    revid_prep = revid+"|"
    revid_stack += revid_prep
    if n%20 == 0:
        revid_stack_clean = revid_stack[:-1]
        revid_stack_list.append(revid_stack_clean)
        revid_stack = ""

#open a file for writing down the collected data      
f = open("revision_goodfaith_fourmonth.csv", "w", encoding="UTF-8")
csv_f = csv.writer(f)
#write first row
csv_f.writerow(['revid','prediction','prob-true','prob-false'])


#collecting the good-faith quality score using the stacked revid: revid_stack_list
#api_call = ("https://ores.wikimedia.org/v3/scores/enwiki?models=goodfaith&revids={}").format(revid_stack_clean)
n=0
for revid_stack_clean in revid_stack_list:
    #revid_lst = revid_stack_clean.split('|')
    #userid = row['userid']
    #usertype = row['usertype']
    #event = row['event']
    #api
    api_call = ("https://ores.wikimedia.org/v3/scores/enwiki?models=goodfaith&revids={}").format(revid_stack_clean)#636074156
    response=urllib.request.urlopen(api_call)
    str_response=response.read().decode('utf-8')
    responsedata = json.loads(str_response)
    #responsedata['enwiki']['scores'].keys()
    page_id_lst = list(responsedata['enwiki']['scores'].keys())
    for page_id in page_id_lst:
        score_data = responsedata['enwiki']['scores'][page_id]['goodfaith'].get('score','error')
        if score_data != "error": 
            #error_msg = responsedata['enwiki']['scores'][page_id]['goodfaith']['error'][message]
            #csv_f.writerow([ page_id, prediction, prob_true, prob_false])
            prediction = score_data['prediction']
            prob_true = score_data['probability']['true']
            prob_false = score_data['probability']['false']  
            #print ([ page_id, prediction, prob_true, prob_false])
            csv_f.writerow([ page_id, prediction, prob_true, prob_false])
    n+=1
    if n%10==0:
        print (n) 

f.close()



##################c######################################################
##################c######################################################
###collecting whether the revision is reverted ########

import mwapi, mwreverts.api

# Gather a page's revisions from the API
session = mwapi.Session("https://en.wikipedia.org", user_agent="mwreverts basic usage script")


#An edit can reverting other edits, it can be reverted, or it can be reverted_to by another edit.
def print_revert_status(rev_id, reverting, reverted, reverted_to):
    """Prints a nice, pretty version of a revert status."""
    print(str(rev_id) + ":")
    if reverting is not None:
        print(" - reverting {0} other edits".format(len(reverting.reverteds)))
    if reverted is not None:
        print(" - reverted in {revid} by {user}".format(**reverted.reverting))
    if reverted_to is not None:
        print(" - reverted_to in {revid} by {user}".format(**reverted_to.reverting))

reverting, reverted, reverted_to = mwreverts.api.check(session, 616034852, rvprop={'user'})
print_revert_status(616034852, reverting, reverted, reverted_to)
reverted.reverting


#whether reverted, 1=yes
def revert_status(rev_id, reverted):
    reverting, reverted, reverted_to = mwreverts.api.check(session, rev_id, rvprop={'user'})
    if reverted is not None: 
        return 1
    else: 
        return 0

#using the contribution data
qual_data = pd.read_csv("revision_goodfaith_fourmonth.csv", encoding = "ISO-8859-1")
qual_data.columns.values
qual_data = qual_data.drop_duplicates()
len(set(list(qual_data['revid'])))

revert_dict = {}
n=0
for index, row in qual_data.iterrows():
    n+=1
    revid = row['revid']
    try:
        revert_mark = revert_status(revid, reverted)
        revert_dict[revid]=revert_mark
    except mwapi.errors.APIError:
        revert_dict[revid]= -1 #error
    if n%50==0: 
        print (n)
    
revert_data = pd.DataFrame.from_dict(revert_dict, orient='index')
revert_data.reset_index(inplace=True)
revert_data = revert_data.rename(columns={'index': 'revid'})
revert_data = revert_data.rename(columns={0: 'reverted'})
revert_data.columns.values
revert_data.to_csv("revert_data.csv", index=False)



##################c######################################################
#other sample code of collecting detailed reverted information
##################c######################################################
def revertInfo(rev_id):
    reverting, reverted, reverted_to = mwreverts.api.check(session, rev_id, rvprop={'user'})
    if reverted is not None:
        reverted_info = reverted.reverting
        revertedby_revid = reverted_info['revid']
        revertedby_parentid = reverted_info['parentid']
        reverted_pageid = reverted_info['page']['pageid']
        reverted_title = reverted_info['page']['title']
        revert_info_lst = [revertedby_parentid, reverted_pageid, reverted_title,revertedby_revid]
        return ([revert_info_lst])

    

a=revertInfo(662176088)


#api: https://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=ids|userid|user|comment|comment&revids=662239560
#https://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=ids|userid|user|comment|comment&revids=654547111


revert_data = pd.read_csv("revert_data.csv", encoding = "ISO-8859-1")
revert_data.columns.values

revert_revids = revert_data.loc[revert_data['reverted']==1]
reverted_revid_lst = list(revert_revids['revid'])
len(set(reverted_revid_lst))


revert_info_dict = {}
n=0
for revid in reverted_revid_lst:
    n+=1
    try:
        revert_info = revertInfo(revid)
        revert_info_dict[revid]=revert_info
    except mwapi.errors.APIError:
        revert_dict[revid]= [] #error
    if n%50==0: 
        print (n)

pickle.dump( revert_info_dict, open( "revert_info_dict.p", "wb" ) )



keys = []
list1 = [] #revertedby_parentid
list2 = [] # reverted_pageid
list3 = [] # reverted_title
list4 = [] # revertedby_revid

for k in revert_info_dict:
    keys.append(k)
    list1.append(revert_info_dict[k][0][0])
    list2.append(revert_info_dict[k][0][1])
    list3.append(revert_info_dict[k][0][2])
    list4.append(revert_info_dict[k][0][3])

revert_info = pd.DataFrame({ 'revid': keys, 'revertedby_parent_revid': list1, 'reverted_pageid': list2, 'reverted_title': list3, 'revertedby_revid': list4}, index=keys)
revert_info.columns.values
columns = ['revid', 'revertedby_parent_revid', 'reverted_pageid', 'reverted_title', 'revertedby_revid']
revert_info = revert_info[columns]
revert_info.to_csv("revert_info.csv", index=True)


##collecting comment for each revert_revid
revertedby_revid_lst =  list4


f = open("revvert_comments_fourmonth.csv", "w", encoding="UTF-8")
csv_f = csv.writer(f)
#write first row

csv_f.writerow(['revertedby_revid','reverted_byrevid','userid','user', 'parentid','comment'])


#api_call = ("https://ores.wikimedia.org/v3/scores/enwiki?models=goodfaith&revids={}").format(revid_stack_clean)

# read revid to collect the comments
n=0
for revertedby_revid in revertedby_revid_lst:
    api_call = ("https://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=ids|userid|user|comment&revids={}&format=json").format(revertedby_revid)#636074156
    response=urllib.request.urlopen(api_call)
    str_response=response.read().decode('utf-8')
    responsedata = json.loads(str_response)
    page_id = list(responsedata['query']['pages'].keys())[0]
    revision_data = responsedata['query']['pages'][page_id]['revisions'][0]
    comment = revision_data['comment'].replace(",","")
    reverted_byrevid = revision_data['revid']
    user = revision_data['user']
    userid = revision_data['userid']
    parentid = revision_data['parentid']
    #print ([ page_id, prediction, prob_true, prob_false])
    csv_f.writerow([ revertedby_revid, reverted_byrevid, userid, user, parentid, comment])
    n+=1
    if n%50==0:
        print (n) 

f.close()

