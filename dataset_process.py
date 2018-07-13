import re
import pickle
import pandas as pd
import csv
import datetime

keepers = ['(Semi-)automated edits',
          'Assessment',
          'Average edits per day',
          'Average edits per month',
          'Average edits per user',
          'Average edits per year',
          'Average time between edits (days)',
          'Bot edits',
          'Characters',
          'Editors',
          'Edits in the past 30 days',
          'Edits in the past 365 days',
          'Edits made by the top 10% of editors',
          'External links',
          'First edit',
          'ID',
          'IP edits',
          'Latest edit',
          'Links from this page',
          'Links to this page',
          'Minor edits',
          'Page size',
          'Pageviews (60 days)',
          'References',
          'Reverted edits',
          'Sections',
          'Templates',
          'Total edits',
          'Unique references',
          'Words']


def loadPickleData(file_name: str):
    data = pickle.load(open(file_name, 'rb'))
    return (data['en'], data['es'], data['zh'])


def loadMultiLenArticles(file_name: str):
    data_set = []
    en_counter = 0
    es_counter = 0
    cn_counter = 0
    with open(file_name) as csv_file:
        reader = csv.DictReader(csv_file)
        print(type(reader))
        for row in reader:
            entry = {}
            for key in row.keys():
                entry[key] = row[key]
            en_counter += 1
            es_counter = es_counter + 1 if row['es'] == 'True' else es_counter
            cn_counter = cn_counter + 1 if row['zh'] == 'True' else cn_counter
            data_set.append(entry)
    return data_set


def loadInfoboxData(file_name: str):
    data_set = {}
    with open(file_name) as itn_file:
        reader = csv.DictReader(itn_file)
        for row in reader:
            entry = {}
            entry['category'] = row['category']
            entry['has_infobox'] = row['has_infobox']
            entry['infobox'] = row['infobox_type']
            data_set[row['article']] = entry
    return data_set


def datasetProcessData(articles: list, infobox_data: dict, gstates_en: dict, gstates_es: dict, gstates_cn: dict):
    post_id = 0
    dataset = []
    en_article = 0
    es_article = 0
    cn_article = 0
    for article in articles:
        # infobox info
        # print(article)
        if infobox_data[article['article']]['has_infobox'] == 'TRUE':
            category = infobox_data[article['article']]['category']
        else:
            category = 'None'
        # category = infobox_data[article]['category'] if infobox_data[article]['has_infobox'] == 'TRUE' else 'None'

        # EN version
        entry_en = buildEntryData(article['article'], gstates_en)
        entry_en['post_id'] = post_id
        entry_en['language'] = 'en'
        entry_en['year'] = article['year']
        entry_en['category'] = category
        entry_en['IP edits'] = entry_en['IP edits'].split(' ')[0]
        entry_en['Bot edits'] = entry_en['Bot edits'].split(' ')[0]
        entry_en['Edits made by the top 10% of editors'] = entry_en['Edits made by the top 10% of editors'].split(' ')[0]
        entry_en['Minor edits'] = entry_en['Minor edits'].split(' ')[0]

        # time delta starting point
        if entry_en['First edit'] == '':
            entry_en['time_of_creation'] = 0
        else:
            en_time = datetime.datetime.strptime(entry_en['First edit'][:16], '%Y-%m-%d %H:%M')
            entry_en['time_of_creation'] = (en_time - en_time).days

        en_article += 1
        dataset.append(entry_en)

        
        # ES version
        if article['es'] == 'True':
            es_article += 1
            entry_es = buildEntryData(article['es_title'], gstates_es)
            entry_es['post_id'] = post_id
            entry_es['language'] = 'es'
            entry_es['year'] = article['year']
            entry_es['category'] = category
            entry_es['Bot edits'] = entry_es['Bot edits'].split(' ')[0]
            entry_es['IP edits'] = entry_es['IP edits'].split(' ')[0]
            entry_es['Edits made by the top 10% of editors'] = entry_es['Edits made by the top 10% of editors'].split(' ')[0]
            entry_es['Minor edits'] = entry_es['Minor edits'].split(' ')[0]

            # time delta starting point
            if entry_es['First edit'] == '':
                entry_es['time_of_creation'] = ''
            else:
                es_time = datetime.datetime.strptime(entry_es['First edit'][:16], '%Y-%m-%d %H:%M')
                entry_es['time_of_creation'] = (es_time - en_time).days

            dataset.append(entry_es)
        
        # CN version
        if article['zh'] == 'True':
            cn_article += 1
            entry_cn = buildEntryData(article['zh_title'], gstates_cn)
            entry_cn['post_id'] = post_id
            entry_cn['language'] = 'cn'
            entry_cn['year'] = article['year']
            entry_cn['category'] = category
            entry_cn['Bot edits'] = entry_cn['Bot edits'].split(' ')[0]
            entry_cn['IP edits'] = entry_cn['IP edits'].split(' ')[0]
            entry_cn['Edits made by the top 10% of editors'] = entry_cn['Edits made by the top 10% of editors'].split(' ')[0]
            entry_cn['Minor edits'] = entry_cn['Minor edits'].split(' ')[0]

            # time delta starting point
            if entry_cn['First edit'] == '':
                entry_cn['time_of_creation'] = ''
            else:
                cn_time = datetime.datetime.strptime(entry_cn['First edit'][:16], '%Y-%m-%d %H:%M')
                entry_cn['time_of_creation'] = (cn_time - en_time).days

            dataset.append(entry_cn)

        # post_id process
        post_id += 1
    

    print("en total: ", en_article)
    print("es total: ", es_article)
    print("cn total: ", cn_article)
    print("total article: ", en_article+es_article+cn_article)
    return dataset
        

def buildEntryData(article: str, gstate: dict):
    result = {'article': article}
    if article in gstate.keys():
        for keeper_key in keepers:
            if keeper_key in gstate[article].keys():
                result[keeper_key] = gstate[article][keeper_key]
            else:
                result[keeper_key] = ''
    else:
        for key in keepers:
            result[key] = ''

    return result


def dateStroing(data: list, file_name: str):
    df = pd.DataFrame(data)
    df.to_csv(file_name, encoding='utf-8', index=False)


print("--####### starting #######--")
print("--####### loading data #######--")
print("  ####### xtool data #######  ")
en, es, cn = loadPickleData('articles_gstates.p')
print("  ####### posted itn entries #######  ")
articles = loadMultiLenArticles('posted_itn_n.csv')
print("  ####### infobox category data #######  ")
infobox_set = loadInfoboxData('inflbox_itn_set.csv')

print("--####### merging data set #######--")
dataset = datasetProcessData(articles, infobox_set, en, es, cn)

print(" ")
print("--####### merging data set #######--")
dateStroing(dataset, 'process_analysis.csv')