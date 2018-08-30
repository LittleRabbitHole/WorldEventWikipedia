import requests
import pandas as pd
import csv
import sys
import logging

import ArticleFilter as utl
import AfterPostActivity as apa


languages = ['en', 'es']
logging.basicConfig(filename='logs/quality.log', level=logging.DEBUG)

def getRevisionQuality(revid_list: list, language: str, model='goodfaith') -> dict:
    context = language+'wiki'
    url_prefix = 'https://ores.wikimedia.org/v3/scores/' + context + '?models=' + model + '&revids='

    url = url_prefix + combineRevid(revid_list)

    logging.info(url)

    r = apa.getReturnedJSON(url)

    results_dict = getScoreDict(context, r)

    quality_scores = {}

    for revid in revid_list:
        if 'error' in results_dict[str(revid)][model].keys():
            logging.error(results_dict[str(revid)][model]['error'])
            quality_scores[revid] = 0 if results_dict[str(revid)][model]['error']['type'] == 'CommentDeleted' else -1
        else:
            score_dict = results_dict[str(revid)][model]['score'] # 0 for deleted text, -1 for deleted comments, -2 for other
            logging.info(results_dict[str(revid)][model]['score'])
            quality_scores[revid] = score_dict['probability']['true']
    
    return quality_scores



def combineRevid(revid_list: list) -> str:
    combined_list = ''
    for revid in revid_list:
        combined_list += str(revid)
        combined_list += '|'
    
    return combined_list[:-1]


def getScoreDict(context: str, response: dict) -> dict:  
    try:
        return response[context]['scores']
    except KeyError as err:
        if 'error' in response.keys():
            print(response['error'])
            logging.error(response['error'])
        logging.info(response)
        print(response)
        return None


def getQualityScore(dataset: str):
    df_rev_dataset = pd.read_csv(dataset)

    for lang in languages:
        logging.info('starting for revisions in: ' + lang)
        df_rev_dataset_lang = df_rev_dataset.loc[lambda df: df['language'] == lang]
        print(lang, df_rev_dataset_lang.shape[0])

        revids = df_rev_dataset_lang['revid'].tolist()
        
        for chunks in [revids[x:x+4] for x in range(0, len(revids), 4)]:
            rev_quality = getRevisionQuality(revid_list=chunks, language=lang)

            for_store = []
            for rev_id in rev_quality.keys():
                for_store.append({'revid': rev_id, 'quality': rev_quality[rev_id], 'language': lang})

            utl.writeRowsCSV(for_store, fieldnames=['revid', 'quality', 'language'], filenames='data/rev_quality.csv')


getQualityScore('data/rev_pool_candidate.csv')

