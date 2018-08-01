#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 13:40:35 2018
Topic modeling of the Wikipedia itns blurbs
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
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
import collections
import pycountry

wordnet_lemmatizer = WordNetLemmatizer()


def listofContries():
    listCountries = []
    for i in range(len(list(pycountry.countries))):
        name = list(pycountry.countries)[i].name
        name = name.lower().split(', ')
        listCountries+=name
    return listCountries

listCountries = listofContries()


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


def clean_blurb(c):
    #define patterns
    URL_PATTERN=re.compile(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')
    #HASHTAG_PATTERN = re.compile(r'#\w*')
    #MENTION_PATTERN = re.compile(r'@\w*')
    RESERVED_WORDS_PATTERN = re.compile(r'^(RT|FAV)')
    #SMILEYS_PATTERN = re.compile(r"(?:X|:|;|=)(?:-)?(?:\)|\(|O|D|P|S){1,}", re.IGNORECASE)
    NUMBERS_PATTERN = re.compile(r"(^|\s)(\-?\d+(?:\.\d)*|\d+)")

    #clean url, emoji, mention, smiley
    blurb = c['all_blurbs']
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
        #word_lst = [re.sub(r'[^a-zA-Z]+', ' ', s) for s in word_lst1]
        word_lst = [s.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`–~-=_+"}) for s in word_lst1]
        word_lst = [s.replace("'", '') for s in word_lst]
        #remove stop words
        filtered_words = [word for word in word_lst if word not in stopwords.words('english')]
        
        #remove all contries
        filtered_words = [word for word in filtered_words if word not in listCountries] 
        #remove all non-letters
        filtered_stopwords = [re.sub(r'^[^a-zA-Z]+$', '', s) for s in filtered_words]
        filtered_stopwords = list(filter(None, filtered_stopwords))
        
        #remove none
        final_word_lst = list(filter(None, filtered_stopwords))

        #lemm      
        tagged = nltk.pos_tag(final_word_lst)
        lemed_lst = [wordnet_lemmatizer.lemmatize(x[0], get_wordnet_pos(x[1])) for x in tagged]
        
        add_lst = ["n", "u", "s",'united', 'state','italian', 'slovenian', 'american','america','blurb', 's', 'first', 'second', 'third', 'fourth', "two","russia", "russian","000","french","syrian","australian","turkish","zealand","london","africa","japanese","england","f","german","york","2013","san","n","indian", "european", "kingdom", "egyptian"]
        
        final__word_lst = [word for word in lemed_lst if word not in add_lst]

        #rejoin into sentence
        cleanedtext = ' '.join(final__word_lst)
        
        #need to do it again
        clean_lst = cleanedtext.split(' ')
        clean_lst = [re.sub(r'^[^a-zA-Z]+$', '', s) for s in clean_lst]
        clean_lst = [word for word in clean_lst if word not in stopwords.words('english')]
        clean_lst = list(filter(None, clean_lst))
        tagged = nltk.pos_tag(clean_lst)
        clean_lst = [wordnet_lemmatizer.lemmatize(x[0], get_wordnet_pos(x[1])) for x in tagged]
        clean_lst = [word for word in clean_lst if word not in add_lst]
        clean_lst = list(filter(None, clean_lst))
        
        cleanedtext = ' '.join(clean_lst)
        
    else:
        #clean_lst = [""]
        #rejoin into sentence
        cleanedtext = ' '.join(clean_lst)
    
    #return result  
    return cleanedtext

#to get the distribution of the top words and write out
def topWords(blurb_data_clean):
    word_lst = []
    #m = 0
    for blurb in blurb_data_clean:
        #m+=1
        #if m%10000==0: print(m) 
        blurb_lst = blurb.split(" ")
        blurb_lst = [x.replace('"',"").strip() for x in blurb_lst]
        blurb_lst = [x for x in blurb_lst if x]
        word_lst += blurb_lst #24034
    
    
    counter=collections.Counter(word_lst)
    top = counter.most_common(300000)
    
    outString = '"word", "count"'
    i = 0
    for item in top:
        i += 1
        count = str(item[1])
        word = '"{}"'.format(item[0])
        outString += '\n'
        outString += ', '.join([word, count])
    
    with open('/Users/Ang/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEvents&Wikipedia/data/Blurbs_wordsort_v3.csv', 'w') as f:
        f.write(outString)
        f.close()
        

def display_topics(model, feature_names, no_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print ("Topic {}:".format(topic_idx))
        print (" ".join([feature_names[i] for i in topic.argsort()[:-no_top_words - 1:-1]]))


def checkDeath(row):
    if "death of" in row['header'].lower():
        return 1
    else:
        return 0

def checkPosted(row):
    if "[posted]" in row['header'].lower():
        return 1
    else:
        return 0



if __name__ == "__main__":
    itns_data = pd.read_table("/Users/Ang/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEvents&Wikipedia/data/itns_forblurbs.csv", 
                             sep=',', error_bad_lines = False)#7690
    itns_data["posted"] = itns_data.apply(checkPosted, axis=1)
    itns_data_posted = itns_data.loc[itns_data['posted'] == 1] #3151
    blurb_data = itns_data_posted[['year', 'time', 'header', 'article', 'article2',
                                   'blurb', 'altblurb', 'altblurb2','altblurb3', 'altblurb4']]
    blurb_data['blurb'] = blurb_data['blurb'].str.replace(r'<!--.+?-->', '', case=False)
    blurb_data['altblurb'] = blurb_data['altblurb'].str.replace(r'<!--.+?-->', '', case=False)
    blurb_data['altblurb2'] = blurb_data['altblurb2'].str.replace(r'<!--.+?-->', '', case=False)
    blurb_data['altblurb3'] = blurb_data['altblurb3'].str.replace(r'<!--.+?-->', '', case=False)
    blurb_data['altblurb4'] = blurb_data['altblurb4'].str.replace(r'<!--.+?-->', '', case=False)

    blurb_data = blurb_data.fillna(" ")
    #blurb_data = pd.read_table("/Users/Ang/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEvents&Wikipedia/data/itnsblurbs_V2.csv", 
    #                         sep=',', error_bad_lines = False)#3151
    
    blurb_data["Death"] = blurb_data.apply(checkDeath, axis=1)
    blurb_data = blurb_data.loc[blurb_data['Death'] == 0] #3116
    blurb_data.columns.values
    #blurb_data.to_csv("/Users/Ang/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEvents&Wikipedia/data/itnsblurbs_V2.csv")
    
    blurb_data['all_blurbs'] = blurb_data["blurb"] + " " + blurb_data["altblurb"] + ""+ blurb_data["altblurb2"] + ""+ blurb_data["altblurb3"]+ ""+ blurb_data["altblurb4"]
    #blurb_data['all_blurbs'] = blurb_data['all_blurbs'].str.replace(r'<!--.+?-->', '', case=False)
    #blurb_data[['all_blurbs','clean_blurbs']].to_csv("/Users/Ang/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEvents&Wikipedia/data/itnsblurbs_check_v1.csv")
    
    blurb_data['clean_blurbs'] = blurb_data.apply(clean_blurb, axis=1)
    #blurb_data[['all_blurbs','clean_blurbs']].to_csv("/Users/Ang/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEvents&Wikipedia/data/itnsblurbs_check_v1.csv")
    
    blurb_data_clean = blurb_data['clean_blurbs'].tolist()
    #topWords(blurb_data_clean)
    
    # Initialize a CountVectorizer object: count_vectorizer
    # https://medium.com/mlreview/topic-modeling-with-scikit-learn-e80d33668730
    no_features = 1000
    no_topics = 7
    no_top_words = 20
    
    # NMF is able to use tf-idf
    tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, max_features=no_features, stop_words='english')
    tfidf = tfidf_vectorizer.fit_transform(blurb_data_clean)
    tfidf_feature_names = tfidf_vectorizer.get_feature_names()

    # Run NMF
    nmf = NMF(n_components=no_topics, random_state=1, alpha=.1, l1_ratio=.5, init='nndsvd').fit(tfidf)
    display_topics(nmf, tfidf_feature_names, no_top_words)
    
    #predict = nmf.fit_transform(tfidf)
    #topic_comp = nmf.components_
    
    predict = nmf.transform(tfidf)
    predict_df = pd.DataFrame(predict)
    predict_df = predict_df.reset_index(drop=True)
    
    #rejoin back the topic into the blurb dataset
    blurb_df = blurb_data[['year', 'time', 'header', 'article', 'article2', 'all_blurbs','clean_blurbs']].reset_index(drop=True)
    frames = [blurb_df, predict_df]
    result = pd.concat(frames, axis=1)
    result['nwords'] = result['clean_blurbs'].apply(lambda x: len(x.split(" ")))
    result["has_topic"] = result[0]+result[1]+result[2]+result[3]+result[4]+result[5]+result[6]
    result["has_topic_b"] = result["has_topic"] > 0 
    result["has_topic_b"] = result["has_topic_b"].astype("int64")
    
    result["has_topic_b"].sum() 
    
    #write out the blurb data with topic results
    result.to_csv("/Users/Ang/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEvents&Wikipedia/data/results_v1.csv")
    
    # LDA can only use raw term counts for LDA because it is a probabilistic graphical model
    tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=no_features, stop_words='english')
    tf = tf_vectorizer.fit_transform(blurb_data_clean)
    tf_feature_names = tf_vectorizer.get_feature_names()

    # Run LDA
    lda = LatentDirichletAllocation(n_topics=no_topics, max_iter=5, learning_method='online', learning_offset=50.,random_state=0).fit(tf)
    
    display_topics(lda, tf_feature_names, no_top_words)

    
