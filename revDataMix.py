##
# Finial list of fields:
#
# Article id  (article level) !
# Article title (article level) !
# Revid (revision level) 
# Username (revision level)
# Timestamp (revision level)
# Size (revision level)
# Comments (revision level)
# Tags (revision level)
# Language (article level) !
# Category (article level) !
# # of Wiki links (article level)
# # of External links (article level)
# # of references (article level)
# Quality of revision (revision level) (Ang will provide this)
# Topic (from Ang's work) (article level) !
# timestamp of wiki in the news (article level) !
# 
##

import pandas as pd
import csv
import pickle
import logging
import datetime

import AfterPostActivity as apa
import ArticleFilter as utl

logger = logging.getLogger('revDataMix')
logger.setLevel(logging.INFO)

# create console handler and set level to debug
ch = logging.FileHandler('logs/revDataMix_180813.log')
ch.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

# 'application' code
# logger.debug('debug message')
# logger.info('info message')
# logger.warn('warn message')
# logger.error('error message')
# logger.critical('critical message')


df_process_analysis = pd.read_csv('/Users/keyangzheng/Google Drive/WorldEvents&Wikipedia/data/process_data_with_topic.csv')
pickle_folder_path = 'data/pickle/'
header_flag = True
field_names = ['user', 'timestamp', 'references', 'comment', 'tags', 'external_links', 'revid', 'language', 'article_id', 'size', 'post_time', 'category', 'topic', 'post_id', 'wiki_links']
rev_headers = ['revid','user','timestamp','size','comment','tags']

for idx, row in df_process_analysis.iterrows():
    if not apa.articleFilter(row):
        continue
    
    print(row['post_id'], row['language'], row['article'])
    artl_fields = {}
    artl_fields['post_id'] = row['post_id']
    artl_fields['language'] = row['language']

    pickle_file_path = pickle_folder_path + str(row['post_id']) + '_' + row['language'] + '_revisions.p'

    revision_data = pickle.load(open(pickle_file_path , "rb" ))

    artl_fields['article_id'] = row['ID']

    artl_fields['post_time'] = datetime.datetime.strptime(str(row['year']) + ' ' + row['time'], '%Y %B %d').isoformat()
    artl_fields['category'] = row['category']
    artl_fields['topic'] = row['topic']

    if type(revision_data) is not list:
        logger.warn('article ' + row['article'] + ' pickle data format error. post_id: ' + str(row['post_id']) + '_' + row['language']) 

    for rev in revision_data:
        rev_fields = {}
        for key in rev_headers:
            if key in rev.keys():
                rev_fields[key] = rev[key]
            else:
                logger.warn('article: ' + row['article'] + ' revision: ' + str(rev['revid']) + ' missing key: ' + key)
                rev_fields[key] = ''
        
        entry = dict(artl_fields, **rev_fields)
        print(entry)
        entry['wiki_links'] = row['Links from this page']
        entry['external_links'] = row['External links']
        entry['references'] = row['References']

        # entry_prepared = []
        if header_flag:
            header_flag = False
            utl.writeRowsCSV([entry], fieldnames=field_names, filenames='data/article_pool_rev.csv', header=True)
        else:
            utl.writeRowsCSV([entry], fieldnames=field_names, filenames='data/article_pool_rev.csv')



    
