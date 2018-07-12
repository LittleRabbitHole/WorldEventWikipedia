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
    return (data['en'], data['es'], data['cn'])


def loadMultiLenArticles(file_name: str):
    data_set = []
    with open(file_name) as csv_file:
        reader = csv.DictReader(csv_file)
        print(type(reader))
        for row in reader:
            entry = {}
            for key in row.keys():
                entry[key] = row[key]
            data_set.append(entry)
            # data_set.append({'year': row['year'], 'time': row['time'], 'header': row['header'], 'article': row['article'], 'article2': row['article2'], 'blurb': row['blurb'],
            #                  'altblurb': row['altblurb'], 'altblurb2': row['altblurb2'], 'altblurb3': row['altblurb3'], 'altblurb4': row['altblurb4']})
    return data_set


def loadInfoboxData(file_name: str):
    data_set = {}
    with open(file_name) as itn_file:
        reader = csv.DictReader(itn_file)
        for row in reader:
            entry = {}
            entry['category'] = row['category']
            entry['has_infobox'] = row['has_infobox']
            entry['infobox_type'] = row['infobox']
            data_set[row['article']] = entry
    return data_set


def datasetProcessData(articles: list, infobox_data: dict, gstates_en: dict, gstates_es: dict, gstates_cn: dict):
    post_id = 0
    dataset = []
    for article in articles:
        # infobox info
        category = infobox_data[article]['category'] if infobox_data[article]['has_infobox'] == 'TRUE' else 'None'

        # EN version
        entry_en = buildEntryData(article['article'], gstates_en)
        entry_en['post_id'] = post_id
        entry_en['language'] = 'en'
        entry_en['year'] = article['year']
        entry_en['category'] = category

        # time delta starting point
        en_time = datetime.datetime.strptime(entry_en['First edit'][:16], '%Y-%m-%d %H:%M')
        entry_en['time_of_creation'] = (en_time - en_time).days

        dataset.append(entry_en)

        
        # ES version
        if article['es'] == 'TRUE':
            entry_es = buildEntryData(article['es_title'], gstates_es)
            entry_es['post_id'] = post_id
            entry_es['language'] = 'es'
            entry_es['year'] = article['year']
            entry_es['category'] = category

            # time delta starting point
            es_time = datetime.datetime.strptime(entry_es['First edit'][:16], '%Y-%m-%d %H:%M')
            entry_es['time_of_creation'] = (es_time - en_time).days

            dataset.append(entry_es)
        
        # CN version
        if article['zh'] == 'TRUE':
            entry_cn = buildEntryData(article['zh_title'], gstates_cn)
            entry_cn['post_id'] = post_id
            entry_cn['language'] = 'cn'
            entry_cn['year'] = article['year']
            entry_cn['category'] = category

            # time delta starting point
            cn_time = datetime.datetime.strptime(entry_cn['First edit'][:16], '%Y-%m-%d %H:%M')
            entry_cn['time_of_creation'] = (cn_time - en_time).days

            dataset.append(entry_cn)

        # post_id process
        post_id += 1
    
    return dataset
        

def buildEntryData(article: str, gstate: dict):
    result = {'article': article}
    if article in gstate.keys():
        for keeper_key in keepers:
            result[keeper_key] = gstate[article][keeper_key]
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
dateStroing(dataset, process_analysis.csv)