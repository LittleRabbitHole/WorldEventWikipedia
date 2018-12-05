#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  3 10:58:25 2018

quality measure collection and set data

output: qualitymeasures_dataset_r1.csv
    

@author: angli
"""
import pandas as pd
import rev_info_full as rq


def qual_measures(revid, pageid, lang):
    qual_measures = rq.qualityMeasures(revid, pageid, lang)
    #'https://'+lang+'.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&format=json&inprop=url&revids='+str(article_firstedit_ever_revid)
    size = qual_measures["size"] 
    external_links = qual_measures["external_links"] 
    wiki_links = qual_measures["wiki_links"]
    references =  qual_measures["references"]
    section_breadth =  qual_measures["section_breadth"]
    section_depth = qual_measures["section_depth"]
    section_num = qual_measures["section_num"]
    qual_lst = [size, external_links, wiki_links, references, section_breadth, section_depth, section_num]
    return qual_lst


if __name__ == "__main__":
    linkInfo = pd.read_csv("/Users/angli/ANG/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/effort_dataset_r1.csv")

    #write out
    f = open("/Users/angli/ANG/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/qualitymeasures_dataset_r1.csv", "w")
    #write first row, column names
    f.write('postid,lang,postyear,postdatetime,pageid,article_firstedit_ever_date,o0_size,o0_external_links,o0_wiki_links,o0_references,o0_section_breadth,o0_section_depth,o0_section_num,o1_size,o1_external_links,o1_wiki_links,o1_references,o1_section_breadth,o1_section_depth,o1_section_num,o2_size,o2_external_links,o2_wiki_links,o2_references,o2_section_breadth,o2_section_depth,o2_section_num,o3_size,o3_external_links,o3_wiki_links,o3_references,o3_section_breadth,o3_section_depth,o3_section_num,o4_size,o4_external_links,o4_wiki_links,o4_references,o4_section_breadth,o4_section_depth,o4_section_num\n')
    
    i=0
    for ind, row in linkInfo.iterrows():
        i+=1
        if i%50 == 0: print(i)
        
        #post info
        postid, lang, postyear, postdatetime, pageid = str(row['postid']), row['lang'], str(row['postyear']), row['postdatetime'], str(row['pageid'])
        
        #article_firstedit_ever
        article_firstedit_ever_date = row['article_firstedit_ever_date']
        article_firstedit_ever_revid = str(int(row['article_firstedit_ever_revid']))
        if article_firstedit_ever_revid != "-1":
            o0_qual_lst = qual_measures(article_firstedit_ever_revid, pageid, lang)
            o0_lst = [article_firstedit_ever_date] + o0_qual_lst
        else:
            o0_lst = [article_firstedit_ever_date] + 7*[str(-1)]
        
        #first edit
        firstedit_revid = str(int(row['firstedit_revid']))
        if firstedit_revid != "0":
            o1_lst = qual_measures(firstedit_revid, pageid, lang)
        else:
            o1_lst = 7*[str(-1)]
        
       #first day
        endfirstday_revid = str(int(row['endfirstday_revid']))
        if endfirstday_revid != "0":
            o2_lst = qual_measures(endfirstday_revid, pageid, lang)
        else:
            o2_lst = 7*[str(-1)]

        #first week
        endfirstweek_revid = str(int(row['endfirstweek_revid']))
        if endfirstweek_revid != "0":
            o3_lst = qual_measures(endfirstweek_revid, pageid, lang)
        else:
            o3_lst = 7*[str(-1)]

        #first month
        firstmonth_revid = str(int(row['firstmonth_revid']))
        if firstmonth_revid != "0":
            o4_lst = qual_measures(firstmonth_revid, pageid, lang)
        else:
            o4_lst = 7*[str(-1)]
        
        #set together
        quality_5os = [postid, lang, postyear, postdatetime, pageid] + o0_lst + o1_lst + o2_lst + o3_lst + o4_lst
        quality_5os_str = [str(x) for x in quality_5os]
        
        #writeout
        line_string = ",".join(quality_5os_str)+"\n"
        f.write(line_string)
    
    f.close()
        
        
        
        
        
        
        
        