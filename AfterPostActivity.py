##
# Get edit activities from wiki revision records.
#
# revision request:
#  /w/api.php?action=query&prop=revisions&titles=[TITLE]
#             &rvprop=ids%7Ctags%7Cflags%7Ctimestamp%7Cuser%7Csize%7Cparsedcomment%7Ccomment
#             &rvend=[EARLIER TIME]&rvstart=[LATER TIME]&rvlimit=50&format=json&formatversion=2
#
# compare request:
#  /w/api.php?action=compare&fromrev=[REV DIFF BASE ID]&torev=[REV DIFF TARGET ID]
#             &prop=diff%7Ccomment%7Cuser%7Cparsedcomment&format=json&formatversion=2
#
# - The 'diffsize' in Wiki Compare API is the size different between 2 revision's HTML format
#   not the in actural wiki text size, which should be calculated based on the size of every
#   revision.
#
# - The 'parsedcomment' in Wiki Revision API is the raw HTML version of the comment showed in
#   the article's revision page, which has a special character contain information like "section
#   edit" (and the section title), "automatic edit summary". These information is not available
#   in Revision API to be accessed, but seems useful enough to be included. The extraction should
#   be a relatively easy job
#
# - By counting the number of reference items in article's Reference section, we should be able to
#   get the # of unique references. For the # of references, we need to count the actual # of
#   reference marks in the text (or the <ref> tags in wiki text)
##

import csv
import re
import pandas as pd
import datetime as dt
import requests
import pickle
import logging

import ArticleFilter as utl


logging.basicConfig(filename='logs/example.log', level=logging.WARNING)


# check if the current row (pd.Series) represents a recent death event.
def isRecentDeath(row) -> bool:
    return(bool(row['RD']))


# Save data to disk
#  addition -> bool, False (default): save data to a new file; True: save data to an existing file
#  files -> str ('all' or specified file name): which file(s) to save to
#                'all' (default): use when data contain all parts of required fields
#                specified file name: use when data contain a single data field, data will be save to the specified file
#  article -> str, specify the article name when data is targeted at a single article, only when addition is True
#  kind -> str ('csv' or 'pickle') specify what kind of file type to be stored in
# TODO
def saveData(data: dict, files='all', addition=False, article=None, kind='csv'):
    pass


def getRVActivityByDay(article: str, lan: str, day: str) -> dict:
    rv_end = day + "T00:00:00"
    rv_start = day + "T23:59:59"

    return getRVActivityByTimePeriod(article, lan, rv_start, rv_end)

# start: later time point
# end: earlier time point
def getRVActivityByTimePeriod(article: str, lan: str, start: str, end: str) -> dict:
    result = {'edits': 0, 'minor': 0, 'section': 0, 'automatic summary': 0,
              'editors': 0, 'references': 0, 'u_references': 0, 'content_added': 0}
    editor_list = {}

    url = lan + ".wikipedia.com/w/api.php?action=query&prop=revisions&titles=" + \
        article + "&rvprop=ids%7Ctags%7Cflags%7Ctimestamp%7Cuser%7Csize%7Cparsedcomment%7Ccomment\
            &rvend=" + end + "&rvstart=" + start + "&rvlimit=50&format=json&formatversion=2"
    response = utl.returnJsonCheck(requests.get(url))
    try:
        rv_list = response['query']['pages'][0]['revisions']
    except KeyError as err:
        logging.error(err)
        logging.info(response)
        return result
    
    result['edit'] = len(rv_list)
    rv_oldest = rv_list[-1]
    rv_latest = rv_list[0]

    for rv in reversed(rv_list):
        if rv['user'] in editor_list.keys():
            pass
            # editor_list[rv['user']] += 

    return result


def getUniqueRefNum(article: str):
    pass


def getRefNum(article: str):
    pass


def getRVContent(article: str, rvid: str):
    pass


# initialize the specific dict for targeted article
# TODO initialize the dict using data from saved file
def initializeDatafield(article: str, from_file=False) -> dict:
    if from_file:
        return None
    else:
        data_field = {'article': article}
        data_field['edits'] = {'D0': 0, 'BD1': 0, 'BD2': 0, 'BD3': 0, 'BD4': 0, 'BD5': 0, 'BD6': 0,
                               'BD7': 0, 'AD1': 0, 'AD2': 0, 'AD3': 0, 'AD4': 0, 'AD5': 0, 'AD6': 0, 'AD7': 0, 'AM1': 0}
        data_field['minor'] = {'D0': 0, 'BD1': 0, 'BD2': 0, 'BD3': 0, 'BD4': 0, 'BD5': 0, 'BD6': 0,
                               'BD7': 0, 'AD1': 0, 'AD2': 0, 'AD3': 0, 'AD4': 0, 'AD5': 0, 'AD6': 0, 'AD7': 0, 'AM1': 0}
        data_field['section'] = {'D0': 0, 'BD1': 0, 'BD2': 0, 'BD3': 0, 'BD4': 0, 'BD5': 0, 'BD6': 0,
                                 'BD7': 0, 'AD1': 0, 'AD2': 0, 'AD3': 0, 'AD4': 0, 'AD5': 0, 'AD6': 0, 'AD7': 0, 'AM1': 0}
        data_field['automatic summary'] = {'D0': 0, 'BD1': 0, 'BD2': 0, 'BD3': 0, 'BD4': 0, 'BD5': 0, 'BD6': 0,
                                           'BD7': 0, 'AD1': 0, 'AD2': 0, 'AD3': 0, 'AD4': 0, 'AD5': 0, 'AD6': 0, 'AD7': 0, 'AM1': 0}
        data_field['editors'] = {'D0': 0, 'BD1': 0, 'BD2': 0, 'BD3': 0, 'BD4': 0, 'BD5': 0, 'BD6': 0,
                                 'BD7': 0, 'AD1': 0, 'AD2': 0, 'AD3': 0, 'AD4': 0, 'AD5': 0, 'AD6': 0, 'AD7': 0, 'AM1': 0}
        data_field['references'] = {'D0': 0, 'BD1': 0, 'BD2': 0, 'BD3': 0, 'BD4': 0, 'BD5': 0, 'BD6': 0,
                                    'BD7': 0, 'AD1': 0, 'AD2': 0, 'AD3': 0, 'AD4': 0, 'AD5': 0, 'AD6': 0, 'AD7': 0, 'AM1': 0}
        data_field['u_references'] = {'D0': 0, 'BD1': 0, 'BD2': 0, 'BD3': 0, 'BD4': 0, 'BD5': 0, 'BD6': 0,
                                      'BD7': 0, 'AD1': 0, 'AD2': 0, 'AD3': 0, 'AD4': 0, 'AD5': 0, 'AD6': 0, 'AD7': 0, 'AM1': 0}
        data_field['content_added'] = {'D0': 0, 'BD1': 0, 'BD2': 0, 'BD3': 0, 'BD4': 0, 'BD5': 0, 'BD6': 0,
                                       'BD7': 0, 'AD1': 0, 'AD2': 0, 'AD3': 0, 'AD4': 0, 'AD5': 0, 'AD6': 0, 'AD7': 0, 'AM1': 0}
        data_field['editor_work'] = {}

        return data_field


def articleActivityAfterPost():
    df_process_analysis = pd.read_csv('process_analysis.csv')
    for row in df_process_analysis.iterrows():
        if isRecentDeath(row):
            continue

        data_field = initializeDatafield(row['article'])

        post_day = dt.datetime.strptime('%Y %B %d', row['year'] + row['time']) if int(
            row['time_from_post']) < 0 else dt.datetime.strptime('%Y-%M-%d', row['First edit time'][:10])

        for time_delta in range(-7, 8):
            if time_delta < 0 and int(row['time_from_post']) >= 0:
                time_key = 'BD' + str(abs(time_delta))
                for key in ['edits', 'minor', 'section', 'automatic summary', 'editors', 'references', 'u_references', 'content_added']:
                    data_field[key][time_key] = 0
                continue

            target_day = post_day + dt.timedelta(days=time_delta)
            activity = getRVActivityByDay(
                row['article'], row['language'], target_day.isoformat())
            time_key = 'BD' + str(abs(time_delta)) if time_delta < 0 else 'AD' + \
                str(abs(time_delta)) if time_delta > 0 else 'D0'
            for key in activity.keys():
                data_field[key][time_key] = activity[key]
