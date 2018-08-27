import requests
import pandas as pd
import csv
import sys
import logging

import ArticleFilter as utl
import AfterPostActivity as apa


languages = ['en', 'es']

def getRevisionQuality(revid_list: list, language: str, model='goodfaith') -> dict:
    context = language+'wiki'
    url_prefix = 'https://ores.wikimedia.org/v3/scores/' + context + '?models=' + model + '&revids='

    url = combineRevid(revid_list)

    r = apa.getReturnedJSON(url)

    results_dict = getScoreDict(context, r)

    quality_scores = {}

    for revid in revid_list:
        score_dict = results_dict[revid]
        prediction = score_dict['prediction']
        quality_scores['revid'] = score_dict['probability'][prediction]
    
    return quality_scores



def combineRevid(revid_list: list) -> str:
    combined_list = ''
    for revid in revid_list:
        combined_list += revid
        combined_list += '|'
    
    return combined_list[:-1]


def getScoreDict(context: str, response: dict) -> dict:  
    try:
        return response[context]['score']
    except KeyError as err:
        if 'error' in response.keys():
            print(response['error']['message'])
        # logging.error(err)
        # logging.info(response)
        return None


def getQualityScore(dataset: str):
    df_rev_dataset = pd.read_csv(dataset)

    for lang in languages:
        df_rev_dataset_lang = df_rev_dataset.loc[lambda df: df['language'] == lang]

        revids = df_rev_dataset['revid'].tolist()
        
        for chunks in [revids[x:x+100] for x in range(0, len(revids), 20)]:
            rev_quality = getRevisionQuality(revid_list=chunks, language=lang)

            for_store = []
            for rev_id in rev_quality.keys():
                for_store.append({'revid': rev_id, 'quality': rev_quality['rev_id']})

            utl.writeRowsCSV(for_store, fieldnames=['revid', 'quality'], filenames='rev_quality.csv')




