#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 12:58:16 2018


grap location from info box:

    parsing info box to get the location
    https://github.com/siznax/wptools/wiki

@author: angli
"""
import pandas as pd
#import urllib
#import infoboxGrabbing as wpinfo
import wptools
import pickle


def checkLocKeys(key_lst):
    checkstrlst = ['site', 'coordinate','map']
    outlockeys = []
    for key in key_lst:
        for chsckstr in checkstrlst:
            if chsckstr in key:
                outlockeys.append(key)
    return outlockeys



def locInfobox(data):
    loc_info_data = {}
    
    i=0
    for index, row in data.iterrows():
        i+=1
        if i%50 == 0: print (i)
        postid = row['postid']
        
        #first level key: postid
        loc_info_data[postid] = {}
        
        #second level keys: en_title, info_location, info_relates
        pagetitle = str(row["en_title"])
        loc_info_data["en_title"] = pagetitle
        
        page = wptools.page(pagetitle)#info box
        page.get_parse()
        infocontent = page.data.get('infobox')
        info_location = [None,None,None]
        info_relates = ""
        if infocontent is not None:
            key_lst = list(infocontent.keys())
            if "location" in key_lst:
                location = infocontent.get("location")
                info_location[0] = location
            elif "locale" in key_lst:
                locale = infocontent.get("locale")
                info_location[1] = locale
            elif "nation" in key_lst:
                nation = infocontent.get("nation")
                info_location[2] = nation
            else:
                other_lockeys = checkLocKeys(key_lst)
                if len(other_lockeys) != 0:
                    for lockey in other_lockeys:
                        loc_item = infocontent.get(lockey)
                        info_relates = info_relates + "||" + loc_item
        loc_info_data["info_location"] = info_location
        loc_info_data["info_relates"] = info_relates      
    
    return loc_info_data

data = pd.read_csv("/Users/angli/ANG/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/post_articles_set_r1.csv")
loc_info_data = locInfobox(data)
pickle.dump( loc_info_data, open( "/Users/angli/ANG/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/post_location.p", "wb" ) )
