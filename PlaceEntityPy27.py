#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  2 22:44:26 2018

@author: Ang
"""

import pandas as pd
import nltk

nltk.downloader.download('maxent_ne_chunker')
nltk.downloader.download('words')
nltk.downloader.download('treebank')
nltk.downloader.download('maxent_treebank_pos_tagger')


import geograpy

data = pd.read_table("/Users/Ang/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEvents&Wikipedia/data/results_v1.csv", 
                             sep=',', error_bad_lines = False)  

data.columns.values

data['header'].iloc[0]

text = 'China is a country'
places = geograpy.get_place_context(text = text)
places.countries

