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


logging.basicConfig(filename='logs/example.log', level=logging.INFO)


# check if the current row (pd.Series) represents a recent death event.
def isRecentDeath(row) -> bool:
    return(bool(row['RD']))


def getReturnedJSON(url: str, continue_pointer=None):
    if not continue_pointer:
        return(utl.returnJsonCheck(requests.get(url)))
    else:
        return(utl.returnJsonCheck(requests.get(url + continue_pointer)))


# Save data to disk
#  addition -> bool, False (default): save data to a new file; True: save data to an existing file
#  article -> str, specify the article name when data is targeted at a single article, only when addition is True
#  kind -> str ('csv' or 'pickle') specify what kind of file type to be stored in
# TODO
def saveData(data: list, file, addition=False, article=None, kind=['csv']):
    if 'pickle' in kind:
        pickle.dump(data, open('data/pickle/' + file + '.p', 'wb'))

    fieldnames = ["revid","parentid","minor","user","timestamp","size","comment","parsedcomment","suppressed","anon","commenthidden","tags"]
    if 'csv' in kind:
        if len(data) == 0:
            logging.warning(file)
            return
        with open('data/csv/' + file + '.csv', 'w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames)
            writer.writeheader()
            for item in data:
                diff = set(item.keys()) - set(fieldnames)
                if not len(diff) == 0:
                    for key in list(diff):
                        item.pop(key)
                writer.writerow(item)


def getRVRawData(article: str, lan:str, old: dt.datetime, new: dt.datetime):
    end = old.isoformat()# + 'T00:00:01'
    start = new.isoformat()# + 'T23:59:59'
    lan = 'zh' if lan == 'cn' else lan
    article = article.replace(" ", '%20')
    article = article.split('#')[0] if '#' in article else article
    url = 'https://' + lan + ".wikipedia.org/w/api.php?action=query&prop=revisions&titles=" + article + "&rvprop=ids%7Ctags%7Cflags%7Ctimestamp%7Cuser%7Csize%7Cparsedcomment%7Ccomment&rvend=" + end + "&rvstart=" + start + "&rvlimit=500&format=json&formatversion=2"
    logging.info(url)
    rv_list = []
    continue_flag = True
    continue_pointer = None

    while continue_flag:
        response = getReturnedJSON(url, continue_pointer)
        if 'continue' not in response.keys():
            continue_flag = False
        else:
            continue_flag = True
            continue_pointer = '&rvcontinue=' + response['continue']['rvcontinue']
            logging.info(continue_pointer)

        if 'normalized' in response['query'].keys():
            continue_flag = True
            article = response['query']['normalized'][0]['to']
            url = 'https://' + lan + ".wikipedia.org/w/api.php?action=query&prop=revisions&titles=" + article + "&rvprop=ids%7Ctags%7Cflags%7Ctimestamp%7Cuser%7Csize%7Cparsedcomment%7Ccomment&rvend=" + end + "&rvstart=" + start + "&rvlimit=500&format=json&formatversion=2"
            continue

        try:
            rv_list += response['query']['pages'][0]['revisions']
            logging.info(len(rv_list))
        except KeyError as err:
            logging.error(err)
            logging.info(response)
            return rv_list
    
    return rv_list



def getRVActivityByDay(article: str, lan: str, day: str) -> dict:
    rv_end = day + "T00:00:00"
    rv_start = day + "T23:59:59"

    return getRVActivityByTimePeriod(article, lan, rv_start, rv_end)


# start: later time point
# end: earlier time point
def getRVActivityByTimePeriod(article: str, lan: str, start: str, end: str) -> dict:
    result = {'edits': 0, 'minor': 0, 'section': 0, 'automatic summary': 0, 'anon': 0,
              'editors': 0, 'references': 0, 'u_references': 0, 'content_add': 0, 'content_del': 0}
    editor_list = {}

    url = lan + ".wikipedia.com/w/api.php?action=query&prop=revisions&titles=" + \
        article + "&rvprop=ids%7Ctags%7Cflags%7Ctimestamp%7Cuser%7Csize%7Cparsedcomment%7Ccomment\
            &rvend=" + end + "&rvstart=" + start + "&rvlimit=50&format=json&formatversion=2"

    rv_list = []
    continue_flag = True
    continue_pointer = None

    while continue_flag:
        response = getReturnedJSON(url, continue_pointer)
        if 'continue' not in response.keys():
            continue_flag = False
        else:
            continue_flag = True
            continue_pointer = '&rvcontinue=' + \
                response['continue']['rvcontinue']
            logging.info(continue_pointer)

        try:
            rv_list.append(response['query']['pages'][0]['revisions'])
        except KeyError as err:
            logging.error(err)
            logging.info(response)
            return result

    # edits
    result['edits'] = len(rv_list)

    rv_oldest = rv_list[-1]
    rv_latest = rv_list[0]

    rv_base_id = str(rv_oldest['parentid'])
    rv_base_size_url = lan + ".wikipedia.com/w/api.php?action=query&prop=revisions&titles=" + \
        article + "&rvprop=size&rvendid=" + rv_base_id + "&rvstartid=" + rv_base_id + \
        "&rvlimit=50&format=json&formatversion=2"
    rv_base_size = getReturnedJSON(rv_base_size_url)[
        'query']['pages'][0]['revisions'][0]['size']

    # reference + unique reference
    result['reference'], result['unique reference'] = rvReferenceHandling(
        article, rv_oldest['revid'], rv_latest['revid'])

    for rv in reversed(rv_list):
        # content changes
        size_delta = rv['size'] - rv_base_size
        if size_delta > 0:
            result['content_add'] += size_delta
        else:
            result['content_del'] += abs(size_delta)

        # editor work + editors
        if rv['user'] in editor_list.keys():
            editor_list[rv['user']]['edits'] += 1
            editor_list[rv['user']]['changes'] += abs(size_delta)
        else:
            editor_list[rv['user']]['edits'] = 1
            editor_list[rv['user']]['changes'] = abs(size_delta)

        # minor
        if rv['minor']:
            result['minor'] += 1

        # anonimous
        if 'anon' in rv.keys():
            result['anon'] += 1

        # section
        if '→' in rv['prasedcomment']:
            result['section'] += 1

        # automatic summary
        if '←' in rv['prasedcomment']:
            result['automatic summary'] += 1

    result['editors'] = len(editor_list.keys())
    result['editor_work'] = editor_list

    return result


# TODO
def getUniqueRefNum(content: str) -> int:
    return 0


# TODO
def getRefNum(content: str) -> int:
    return 0


# return (ref_delta, uref_delta)
def rvReferenceHandling(article: str, rv_oldest_id: int, rv_latest_id: int) -> (int, int):
    content_old = getRVContent(article, rv_oldest_id)
    content_new = getRVContent(article, rv_latest_id)

    uref_delta = getUniqueRefNum(content_new) - getUniqueRefNum(content_old)
    ref_delta = getRefNum(content_new) - getRefNum(content_old)

    return (ref_delta, uref_delta)


# TODO
def getRVContent(article: str, rv_id: str) -> str:
    return ""


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
        data_field['anon'] = {'D0': 0, 'BD1': 0, 'BD2': 0, 'BD3': 0, 'BD4': 0, 'BD5': 0, 'BD6': 0,
                               'BD7': 0, 'AD1': 0, 'AD2': 0, 'AD3': 0, 'AD4': 0, 'AD5': 0, 'AD6': 0, 'AD7': 0, 'AM1': 0}
        data_field['editors'] = {'D0': 0, 'BD1': 0, 'BD2': 0, 'BD3': 0, 'BD4': 0, 'BD5': 0, 'BD6': 0,
                                 'BD7': 0, 'AD1': 0, 'AD2': 0, 'AD3': 0, 'AD4': 0, 'AD5': 0, 'AD6': 0, 'AD7': 0, 'AM1': 0}
        data_field['references'] = {'D0': 0, 'BD1': 0, 'BD2': 0, 'BD3': 0, 'BD4': 0, 'BD5': 0, 'BD6': 0,
                                    'BD7': 0, 'AD1': 0, 'AD2': 0, 'AD3': 0, 'AD4': 0, 'AD5': 0, 'AD6': 0, 'AD7': 0, 'AM1': 0}
        data_field['u_references'] = {'D0': 0, 'BD1': 0, 'BD2': 0, 'BD3': 0, 'BD4': 0, 'BD5': 0, 'BD6': 0,
                                      'BD7': 0, 'AD1': 0, 'AD2': 0, 'AD3': 0, 'AD4': 0, 'AD5': 0, 'AD6': 0, 'AD7': 0, 'AM1': 0}
        data_field['content_add'] = {'D0': 0, 'BD1': 0, 'BD2': 0, 'BD3': 0, 'BD4': 0, 'BD5': 0, 'BD6': 0,
                                     'BD7': 0, 'AD1': 0, 'AD2': 0, 'AD3': 0, 'AD4': 0, 'AD5': 0, 'AD6': 0, 'AD7': 0, 'AM1': 0}
        data_field['content_del'] = {'D0': 0, 'BD1': 0, 'BD2': 0, 'BD3': 0, 'BD4': 0, 'BD5': 0, 'BD6': 0,
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
                for key in ['edits', 'minor', 'section', 'automatic summary', 'anon', 'editors', 'references', 'u_references', 'content_add', 'content_del']:
                    data_field[key][time_key] = 0
                continue

            target_day = post_day + dt.timedelta(days=time_delta)
            activity = getRVActivityByDay(
                row['article'], row['language'], target_day.isoformat())
            time_key = 'BD' + str(abs(time_delta)) if time_delta < 0 else 'AD' + \
                str(abs(time_delta)) if time_delta > 0 else 'D0'
            for key in activity.keys():
                data_field[key][time_key] = activity[key]


def getRawData():
    df_process_analysis = pd.read_csv('process_analysis.csv')
    for post_id in range(0, 3500):
        df_article_group = df_process_analysis.loc[lambda df: df['post_id'] == post_id]
        if not articleGroupFilter(df_article_group):
            continue
        logging.info('post_id = ' + str(post_id))
        for idx, row in df_article_group.iterrows():
            start_day = dt.datetime.strptime(row['First edit time'][:10], '%Y-%m-%d')

            post_day = dt.datetime.strptime(str(row['year']) + " " + row['time'], '%Y %B %d') if int(row['time_from_post']) < 0 else start_day

            end_day = post_day + dt.timedelta(days=31)

            rv_list = getRVRawData(row['article'], row['language'], old=start_day, new=end_day)
            # print(len(rv_list))

            saveData(rv_list, file=str(row['post_id']) + '_' + row['language'] + '_revisions', kind=['csv', 'pickle'])


def getRawDataISO():
    df_process_analysis = pd.read_csv('process_analysis.csv')
    # for post_id in range(0, 3500):
    #     df_article_group = df_process_analysis.loc[lambda df: df['post_id'] == post_id]
    #     if not articleFilter(df_article_group):
    #         continue
    #     logging.info('post_id = ' + str(post_id))
    for idx, row in df_process_analysis.iterrows():
        if not articleFilter(row):
            continue

        start_day = dt.datetime.strptime(row['First edit time'][:10], '%Y-%m-%d')

        post_day = dt.datetime.strptime(str(row['year']) + " " + row['time'], '%Y %B %d') if int(row['time_from_post']) < 0 else start_day

        end_day = post_day + dt.timedelta(days=31)

        rv_list = getRVRawData(row['article'], row['language'], old=start_day, new=end_day)
        # print(len(rv_list))

        saveData(rv_list, file=str(row['post_id']) + '_' + row['language'] + '_revisions', kind=['csv', 'pickle'])



def articleGroupFilter(df_articles: pd.DataFrame):
    if df_articles.shape[0] < 1:
        return False

    # print(df_articles.dtypes)
    for idx, row in df_articles.iterrows():
        if articleFilter(row):
            return True
        # print(type(row['RD']))
        # if row['RD']:
        #     return False

        # if row['time_from_post'] < 7 and row['time_from_post'] > -7:
        #     print(str(row['post_id']) + ' ' + row['language'] + ' ' + str(row['time_from_post']))
        #     return True

    return False


def articleFilter(article):
    if article['RD']:
        return False
    
    if article['time_from_post'] in range(-6, 7):
        return True
    
    return False


getRawDataISO()

# df = pd.read_csv('process_analysis.csv')
# counter = 0
# for idx,row in df.iterrows(): #681+366+411
#     if row['language'] in ['en','es']:
#         continue

#     if row['RD']:
#         continue
    
#     if row['time_from_post'] in range(-6, 7):
#         print(row['time_from_post'])
#         counter += 1 

# for post_id in range(0, 3500): #1172
#         df_article_group = df.loc[lambda df: df['post_id'] == post_id]
#         if articleFilter(df_article_group):
#             counter['total'] += df_article_group.shape[0]
#             logging.info(str(post_id) + " True, added articles: " + str(df_article_group.shape[0]) + " Total articles: " + str(counter))
#             for idx, row in df_article_group.iterrows():
#                 counter[row['language']] += 1
#                 logging.info(str(post_id) + " language: " + row['language'])
#         else:
#             logging.info(str(post_id) + " False, discard articles: " + str(df_article_group.shape[0]))
#             for idx, row in df_article_group.iterrows():
#                 # counter[row['language']] += 1
#                 logging.info(str(post_id) + " language: " + row['language'] + " " + str(row['time_from_post']))
            

# print(counter)
