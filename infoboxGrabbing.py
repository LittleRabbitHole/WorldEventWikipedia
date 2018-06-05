"""
Created on Mon Jun  4 15:48:17 2018

@author: Keyang
"""

import requests
import re
import csv
import ArticleFilter as utl

def getInfobox(title: str):
    r_url = "https://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles=" + title + "&rvprop=timestamp%7Cuser%7Ccomment%7Ccontent&formatversion=2&format=json"
    r = requests.get(r_url)
    result = utl.returnJsonCheck(r)
    content = result[0]['revisions']['content']

    # get the infobox type
    infobox_title = ""
    has_infobox = False
    for infobox_split in re.split(r'(Infobox .+?\n)', content):
        # print(itn_split)
        if re.match(r'(Infobox .+?\n)', infobox_split):
            infobox_title = infobox_split
            has_infobox = True
            break
    infobox_type = infobox_title.split(" ", 1)[1]

    return (has_infobox, infobox_type.strip())

def loadDataSet(file_name: str):
    data_set = []
    with open(file_name) as csv_file:
        reader = csv.DictReader(csv_file)
        print(type(reader))
        for row in reader:
            data_set.append({'year':row['year'], 'time':row['time'], 'header':row['header'], 'article':row['article'], 'article2':row['article2']})
    return data_set
