#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  1 19:32:21 2018

@author: jiajunluo
take data into structure
[postid, lang, postyear, postdatetime, pageid]
+
[totaledits_byall, totaledits_byregistered, unique_all_editors,unique_registered_editors, 
total_size_added, sizeadded_byregistered]  
+ 
[firstedit_revid, endfirstday_revid, endfirstweek_revid, firstmonth_revid]
            
"""
import pandas as pd
import pickle
import rev_info_full as rev
from datetime import datetime, timedelta


if __name__ == "__main__":
    #[postid, "en", postyear, postdate, postdatetime, en_pageid, {all revis}]
    articles_revis = pickle.load( open( "/Users/jiajunluo/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/article_revisions_list_6739.p", "rb" ) )
    
    #write out
    f = open("/Users/jiajunluo/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/effort_dataset_r1.csv", "w")
    #write first row
    f.write('postid,lang,postyear,postdatetime,pageid,totaledits_byall,totaledits_byregistered,unique_all_editors,unique_registered_editors,total_size_added,sizeadded_byregistered,firstedit_revid,endfirstday_revid,endfirstweek_revid,firstmonth_revid\n')
    
    i=0
    for article_post in articles_revis:
        i+=1
        if i%100==0: print(i)
        postid, lang, postyear, postdatetime, pageid = article_post[0], article_post[1], article_post[2], article_post[4], article_post[5]
        posttime = datetime.strptime(postdatetime,'%Y-%m-%d')
        row_base = [str(postid), lang, postyear, postdatetime, str(pageid)]
        all_revis = article_post[6]
        if len(all_revis) !=0:
            tst = pd.DataFrame.from_dict(all_revis).sort_values(by=['revid'])
            tst["sizediff"] = tst['size'] - tst['size'].shift(1)
            tst['postdate'] = posttime
            tst['timestamp'] = pd.to_datetime(tst['timestamp'], format= '%Y-%m-%dT%H:%M:%SZ')
            tst['index'] = tst['timestamp']
            tst = tst.set_index('index')
            
            firstedit_revid = str(tst['revid'].iloc[0])
            firstmonth_revid = str(tst['revid'].iloc[-1])
            endfirstday_revid = str(tst.resample('1D').max().iloc[0]["revid"])
            endfirstweek_revid = str(tst.resample('7D').max().iloc[0]["revid"]) 
            
            totaledits_byall = str(len(tst['revid']))
            unique_all_editors = str(len(tst[['user', 'userid']].drop_duplicates())) if tst.get(['user', 'userid']) is not None else str(len(tst[['userid']].drop_duplicates()))
            totaledits_byregistered = str(len(tst['revid'].loc[tst['userid'] > 0]))
            unique_registered_editors = str(len(tst[['userid']].drop_duplicates()) -1)
            total_size_added = str(tst['size'].iloc[-1] - tst['size'].iloc[0])
            sizeadded_byregistered = str(tst['sizediff'].loc[tst['userid'] > 0].sum())
            article_row = row_base + [totaledits_byall, totaledits_byregistered, unique_all_editors,unique_registered_editors, total_size_added, sizeadded_byregistered]  + [firstedit_revid, endfirstday_revid, endfirstweek_revid, firstmonth_revid]
                
            line_string = ",".join(article_row)+"\n"
            f.write(line_string)
        else:
            article_row = row_base + 10*[str(0)]
            line_string = ",".join(article_row)+"\n"
            f.write(line_string)
    f.close()        
            
        