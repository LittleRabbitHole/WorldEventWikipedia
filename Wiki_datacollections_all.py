# -*- coding: utf-8 -*-
"""
Created on Fri Sep 29 10:01:00 2017
This is for all the re0usable functions
for import and use for other code
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
import urllib
import pickle
import itertools

#this is to retrive all revisions for one API
# input API and pageTitle
#need to adjust based on the jason data returned and decode
def GetRevisions(API, pageTitle):
    #pageTitle = 'Executive_Order_13769'
    #https://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles=Executive_Order_13769&rvprop=timestamp|user|comment&generator=revisions
    #url = "https://en.wikipedia.org/w/api.php?action=query&format=json&rvdir=newer&rvlimit=500&prop=revisions&rvprop=ids|timestamp|user|userid|comment&titles=" + pageTitle
    url = API + pageTitle
    revisions = []                                        #list of all accumulated revisions
    next = ''                                             #information for the next request
    while True:
        #response = urllib2.urlopen(url + next).read()     #web request
        response=urllib.request.urlopen(url + next)
        str_response=response.read()#.decode('utf-8')
        responsedata = json.loads(str_response)
        page_id = list(responsedata["query"]["pages"].keys())[0]
        revision_data_lst=responsedata['query']['pages'][page_id]['revisions']
        revisions += revision_data_lst  #adds all revisions from the current request to the list

        try:        
            cont = responsedata['continue']['rvcontinue']
        except KeyError:                                      #break the loop if 'continue' element missing
            break

        next = "&rvcontinue=" + cont             #gets the revision Id from which to start the next request

    return revisions

#this is from article get the revision
#from revision, store in dictionary as:
# ... article1: [user, userid], ...
#eliminated bots
def GetAritlceEdiors(article_list):
    alluser_list = {}
    for article in article_list:
        article = article.strip().replace(" ","_")
        revisions = GetRevisions(article)
        users = []
        #m=0
        for item in revisions:
            username = item.get('user','')
            if ('bot' not in username) and ('Bot' not in username) and ('BOT' not in username):
                users.append([item.get('user',''),item.get('userid','')])
    
        user_list = list(list(users for users,_ in itertools.groupby(users)))
        print (article, len(user_list))
        alluser_list[article] = user_list
    return alluser_list


#this is to get each user's information
def GetUserInfo(name):
    wpid =  name
    wpid = wpid.strip()
    #print (rawID)
    wpid_nospace = wpid.replace(" ","_")
    #decode student's name into ascii
    decode_wpid = urllib.parse.quote(wpid_nospace)
    #api
    #api_call = ("https://en.wikipedia.org/w/api.php?action=query&list=users&ususers={}&usprop=editcount|blockinfo|registration|rights|groups|gender&format=json").format(decode_wpid)#Kingsleyta
    api_call = ("https://en.wikipedia.org/w/api.php?action=query&list=users&ususers={}&usprop=editcount|registration|gender&format=json").format(decode_wpid)#Kingsleyta
    response=urllib.request.urlopen(api_call)
    str_response=response.read().decode('utf-8')
    responsedata = json.loads(str_response)
    #try:
    userinfodata=responsedata["query"]["users"][0]#list
    return userinfodata
    


#this is to get each editor's contribution over history
def GetUserContri(name,starttime,endtime):
    wpid =  name
    wpid = wpid.strip()
    #print (rawID)
    #wpid_nospace = wpid.replace(" ","_")
    #decode student's name into ascii
    #decode_wpid = urllib.parse.quote(wpid_nospace)
    decode_wpid = urllib.parse.quote(wpid)
    #api
    #api_call = ("https://en.wikipedia.org/w/api.php?action=query&list=usercontribs&ucstart=2014-01-01T00:00:00Z&ucuser={}&ucdir=newer&ucprop=title|timestamp|size|sizediff|flags&uclimit=500&format=json").format(decode_wpid)#Kingsleyta  
    #use username
    #api_call = ("https://en.wikipedia.org/w/api.php?action=query&list=usercontribs&ucuser={}&ucdir=newer&ucprop=title|timestamp|size|sizediff|flags&uclimit=500&format=json").format(decode_wpid)#Kingsleyta  
    #use userid
    #api_call = ("https://en.wikipedia.org/w/api.php?action=query&list=usercontribs&ucuserids={}&ucdir=newer&ucprop=title|timestamp|ids|size|sizediff|flags&uclimit=500&format=json").format(decode_wpid)#Kingsleyta  
    #use userid, collect only articles,return with revid IDs
    api_call = ("https://en.wikipedia.org/w/api.php?action=query&list=usercontribs&ucuserids={}&ucdir=newer&ucstart={}&ucend={}&ucnamespace=0&ucprop=title|timestamp|ids|size|sizediff|flags&uclimit=500&format=json").format(decode_wpid,starttime,endtime)#Kingsleyta  

    user_contribs = []  
    response=urllib.request.urlopen(api_call)
    str_response=response.read().decode('utf-8')
    responsedata = json.loads(str_response)
    if 'error' in list(responsedata.keys()):
        return "erroruser"
    else:
        next = ''                                           #information for the next request
        m=0
        while True:
            m+=1
            print (m)
            response=urllib.request.urlopen(api_call + next)
            str_response=response.read().decode('utf-8')
            responsedata = json.loads(str_response)
            usercontribsdata=responsedata["query"]["usercontribs"]#list
            user_contribs += usercontribsdata
            try:        
                cont = responsedata['continue']['uccontinue']
            except KeyError:                                      #break the loop if 'continue' element missing
                break
        
            next = "&uccontinue=" + cont             #gets the revision Id from which to start the next request
    return (user_contribs)

