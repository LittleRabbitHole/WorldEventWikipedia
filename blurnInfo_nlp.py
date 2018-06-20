#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 13:40:35 2018

@author: Ang
"""

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.parse import quote
import pandas as pd
import pickle
import re
import string
import html
import nltk
#nltk.download('popular')
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer

wordnet_lemmatizer = WordNetLemmatizer()


#mapping nltk lemmatizer pos taggs
def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN


def clean_blurb(blurb_row):
    #define patterns
    URL_PATTERN=re.compile(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')
    HASHTAG_PATTERN = re.compile(r'#\w*')
    MENTION_PATTERN = re.compile(r'@\w*')
    RESERVED_WORDS_PATTERN = re.compile(r'^(RT|FAV)')
    SMILEYS_PATTERN = re.compile(r"(?:X|:|;|=)(?:-)?(?:\)|\(|O|D|P|S){1,}", re.IGNORECASE)
    NUMBERS_PATTERN = re.compile(r"(^|\s)(\-?\d+(?:\.\d)*|\d+)")

    #clean url, emoji, mention, smiley
    blurb = blurb_row['all_blurbs']
    clean_Url = re.sub(URL_PATTERN, '', blurb)
    clean_UrlRev = re.sub(RESERVED_WORDS_PATTERN, '', clean_Url)
    clean_final = re.sub(NUMBERS_PATTERN, '', clean_UrlRev)
    #lower case
    Text = str(clean_final).replace("N/A","").lower()
    #into list
    clean_lst = Text.split(' ')
    clean_lst = list(filter(None, clean_lst))
    #if not none
    if len(clean_lst) >= 1 and clean_lst[0] != '':
        #final remove leading/trailing puctuation each word
        word_lst1 = [s.strip("`~()?:!.,;'""&*<=+ >#|-/{}%$^@[]") for s in clean_lst]
        #remove non-letter in middle
        word_lst = [re.sub(r'[^a-zA-Z0-9]+', '', s) for s in word_lst1]
        #remove stop words
        filtered_words = [word for word in word_lst if word not in stopwords.words('english')]
        #remove all non-letters
        filtered_stopwords = [re.sub(r'^[^a-zA-Z]+$', '', s) for s in filtered_words]
        #lemm      
        tagged = nltk.pos_tag(filtered_stopwords)
        lemed_lst = [wordnet_lemmatizer.lemmatize(x[0], get_wordnet_pos(x[1])) for x in tagged]
        
        #remove none
        final__word_lst = list(filter(None, lemed_lst))
        #rejoin into sentence
        cleanedtext = ' '.join(final__word_lst)
    else:
        #clean_lst = [""]
        #rejoin into sentence
        cleanedtext = ' '.join(clean_lst)
    
    #return result  
    return cleanedtext


blurb_data = pd.read_table("/Users/Ang/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEvents&Wikipedia/data/blurb_itn.csv", 
                         sep=',', error_bad_lines = False)
blurb_data.columns.values
blurb_data = blurb_data.fillna(" ")
blurb_data['all_blurbs'] = blurb_data["blurb"] + " " + blurb_data["altblurb"] + blurb_data["altblurb2"] + blurb_data["altblurb3"]+ blurb_data["altblurb4"]
blurb_data['clean_blurbs'] = blurb_data.apply(clean_blurb, )