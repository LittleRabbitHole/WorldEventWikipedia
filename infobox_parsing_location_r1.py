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


def checkLocKeys(key_lst_lower):
    checkstrlst = ['site', 'coordinate','map', 'place','capital', 'city', 'country']
    outlockeys_lower = []
    for key in key_lst_lower:
        for chsckstr in checkstrlst:
            if chsckstr in key:
                outlockeys_lower.append(key)
    return outlockeys_lower



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
        loc_info_data[postid]["en_title"] = pagetitle
        
        page = wptools.page(pagetitle)#info box
        page.get_parse()
        infocontent = page.data.get('infobox')
        
        loc_info_data[postid]['country_code'] = ""
        loc_info_data[postid]['country'] = ""
        loc_info_data[postid]['residence'] = ""
        loc_info_data[postid]["info_location"] = [None,None,None]
        loc_info_data[postid]["info_relates"] = []
        if infocontent is not None:
            key_lst = list(infocontent.keys())
            key_lst_lower = [x.lower() for x in key_lst]
            checked_keys = []
            if "location" in key_lst_lower:
                x = key_lst[key_lst_lower.index("location")]
                checked_keys.append(x)
                loc_info_data[postid]["info_location"][0] = infocontent.get(x)
            if "locale" in key_lst:
                y = key_lst[key_lst_lower.index("locale")]
                checked_keys.append(y)
                loc_info_data[postid]["info_location"][1] = infocontent.get(y)
            if "nationality" in key_lst:
                z = key_lst[key_lst_lower.index("nationality")]
                checked_keys.append(z)
                loc_info_data[postid]["info_location"][2] = infocontent.get(z)
            if "country_code" in key_lst:
                a = key_lst[key_lst_lower.index("country_code")]
                checked_keys.append(a)
                loc_info_data[postid]["country_code"] = infocontent.get(a)
            if "country" in key_lst:
                b = key_lst[key_lst_lower.index("country")]
                checked_keys.append(b)
                loc_info_data[postid]["country"] = infocontent.get(b)
            if "residence" in key_lst:
                c = key_lst[key_lst_lower.index("residence")]
                checked_keys.append(c)
                loc_info_data[postid]["residence"] = infocontent.get(c)
            
            other_lockeys_lower = checkLocKeys(key_lst_lower)
            if len(other_lockeys_lower) != 0:
                for lockey_lower in other_lockeys_lower:
                    lockey = key_lst[key_lst_lower.index(lockey_lower)]
                    loc_item = infocontent.get(lockey)
                    loc_info_data[postid]["info_relates"].append(loc_item)
    
    return loc_info_data

data = pd.read_csv("/Users/jiajunluo/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/post_articles_set_r1.csv")
loc_info_data = locInfobox(data)
pickle.dump( loc_info_data, open( "/Users/jiajunluo/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/post_loc_info.p", "wb" ) )
