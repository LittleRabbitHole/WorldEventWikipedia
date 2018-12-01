#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 23:09:23 2018

@author: jiajunluo
"""

import pickle
import pandas as pd


f = open('/Users/jiajunluo/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/post_article_xtools.p', 'rb')   # 'r' for reading; can be omitted
all_articles = pickle.load(f)         # load file content as mydict
f.close()

<<<<<<< HEAD
all_articles = pickle.load(f)         # load file content as mydict
f.close()

>>>>>>> 1e2b73220ec30afae502cad05d94c2ba727703cb
