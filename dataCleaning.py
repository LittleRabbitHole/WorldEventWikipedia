import pandas
import re
import csv
import requests
import math
import ArticleFilter as utl
import infoboxGrabbing as infobox


def getMultiLang(lang_link_list: list, lang_list=['en', 'es'], titles=False) -> bool:
    # lang_list = ['en', 'es']
    counter = 0
    langs = {}
    for lang in lang_link_list:
        if lang['lang'] in lang_list:
            counter += 1
            langs[lang['lang']] = lang['title']

    return langs


def itnFieldCleanup(article: str, qutation=False, styling=False):
    article_cleaned = re.sub(r'<!--.+?-->', "", article).strip()
    article_cleaned = re.sub(r'<!--', "", article_cleaned).strip()
    article_cleaned = re.sub(r'-->', "", article_cleaned).strip()
    if qutation and styling:
        article_cleaned = article_cleaned[1:-2].strip()
        article_cleaned = re.sub(r'<.+?>', "", article_cleaned).strip()
        article_cleaned = re.sub(r'</.+?>', "", article_cleaned).strip()

    if qutation and re.match(r'^".*"$', article_cleaned):
        article_cleaned = article_cleaned[1:-2].strip()
    if styling and re.match(r'<.+?>.+?</.+?>', article_cleaned):
        article_cleaned = re.sub(r'<.+?>', "", article_cleaned).strip()
        article_cleaned = re.sub(r'</.+?>', "", article_cleaned).strip()

    return article_cleaned


def loadDataSet(file_name: str):
    data_set = []
    with open(file_name) as csv_file:
        reader = csv.DictReader(csv_file)
        print(type(reader))
        for row in reader:
            data_set.append({'year': row['year'], 'time': row['time'], 'header': row['header'], 'article': row['article'], 'article2': row['article2'], 'blurb': row['blurb'],
                             'altblurb': row['altblurb'], 'altblurb2': row['altblurb2'], 'altblurb3': row['altblurb3'], 'altblurb4': row['altblurb4']})
    # return pandas.read_csv(file_name, usecols=['year','time','header','article','article2'], dtype={'year':str,'time':str,'header':str,'article':str,'article2':str})
    return data_set


def isPosted(header: str):
    header = header.strip()
    header = header.lower()
    if "[posted]" in header:
        return True
    else:
        return False


def checkLangLinks(title: str, last=False):
    hasChinese = False
    zh_title = None
    hasEspanish = False
    es_title = None

    request_url = "https://en.wikipedia.org/w/api.php?action=query&format=json&formatversion=2&prop=langlinks&lllimit=500&titles=" + title
    response = requests.get(request_url)

    if utl.apiErrorCheck(response.headers)[0]:
        print("ERROR", id, utl.apiErrorCheck(response.headers)[1])
        return False

    r_json = utl.returnJsonCheck(response)

    if 'missing' in r_json['query']['pages'][0] and r_json['query']['pages'][0]['missing'] and last:
        print(title)
        return checkLangLinks(itnFieldCleanup(title, qutation=True))

    multi_lang_list = r_json['query']['pages'][0]['langlinks'] if 'langlinks' in r_json['query']['pages'][0] else []

    multi_lang_result = getMultiLang(multi_lang_list, lang_list=[
                                     'zh', 'es'], titles=True)
    # print(type(multi_lang_result))
    if len(multi_lang_result.keys()) > 0:
        if 'zh' in dict(multi_lang_result).keys():
            hasChinese = True
            zh_title = dict(multi_lang_result)['zh']
        if 'es' in dict(multi_lang_result).keys():
            hasEspanish = True
            es_title = dict(multi_lang_result)['es']

    return ({'zh': hasChinese, 'zh_title': zh_title}, {'es': hasEspanish, 'es_title': es_title})


def dataCleanMultiLang():
    original_data = loadDataSet("itns.csv")
    posted_counter = 0

    # for itx,row in original_data.iterrows():
    for row in original_data:
        cleaned = []
        if not isPosted(row['header']):
            continue
        posted_counter += 1
        print(row['header'])

        article = itnFieldCleanup(row['article'], styling=True)
        article2 = itnFieldCleanup(row['article2'], styling=True)
        if article != "":
            zh, es = checkLangLinks(article)
            cleaned.append({"year": row['year'], "time": row['time'], "header": row['header'].strip(
            ), "article": article, "zh": zh['zh'], "es": es['es'], "zh_title": zh['zh_title'], "es_title": es['es_title']})

        if article2 != '':
            zh, es = checkLangLinks(article2)
            cleaned.append({"year": row['year'], "time": row['time'], "header": row['header'].strip(
            ), "article": article2, "zh": zh['zh'], "es": es['es'], "zh_title": zh['zh_title'], "es_title": es['es_title']})

        utl.writeRowsCSV(cleaned, fieldnames=[
                         "year", "time", "header", "article", "zh", "es", "zh_title", "es_title"], filenames='posted_itn_n.csv')

    print(posted_counter)


# dataCleanMultiLang()


def infoboxCollecting(source: str, position=None):
    data_set = infobox.loadDataSet(source, position)
    posted_counter = 0
    article_counter = 0

    for row in data_set:
        result = []
        if not isPosted(row['header']):
            continue
        posted_counter += 1
        print(row['header'])

        article = itnFieldCleanup(row['article'])
        article2 = itnFieldCleanup(row['article2'])

        if article != "":
            article_counter += 1
            has_infobox, infobox_type = infobox.getInfobox(article)
            if infobox_type is "missing|":
                continue
            result.append({"year": row['year'], "time": row['time'], "article": article,
                           "itn_header": row['header'], "has_infobox": has_infobox, "infobox_type": infobox_type})

        if article2 != "":
            article_counter += 1
            has_infobox, infobox_type = infobox.getInfobox(article2)
            if infobox_type is "missing|":
                continue
            result.append({"year": row['year'], "time": row['time'], "article": article2,
                           "itn_header": row['header'], "has_infobox": has_infobox, "infobox_type": infobox_type})

        utl.writeRowsCSV(result, fieldnames=[
                         'year', 'time', 'article', 'itn_header', 'has_infobox', 'infobox_type'], filenames='infobox_itn.csv')

# infoboxCollecting('itns.csv', '[Posted] <strike>Replica tomb and </strike>mummies discovered')


def blurbCollecting(source: str):
    raw_data = loadDataSet('itns.csv')
    posted_counter = 0

    for row in raw_data:
        cleaned = []
        if not isPosted(row['header']):
            continue
        posted_counter += 1
        print(row['header'])

        article = itnFieldCleanup(row['article'], qutation=True, styling=True)
        article2 = itnFieldCleanup(
            row['article2'], qutation=True, styling=True)

        header = row['header'].strip()

        blurb = itnFieldCleanup(row['blurb'], qutation=True, styling=True)
        altblurb = itnFieldCleanup(
            row['altblurb'], qutation=True, styling=True) if row['altblurb'] is not "" else ""
        altblurb2 = itnFieldCleanup(
            row['altblurb2'], qutation=True, styling=True) if row['altblurb2'] is not "" else ""
        altblurb3 = itnFieldCleanup(
            row['altblurb3'], qutation=True, styling=True) if row['altblurb3'] is not "" else ""
        altblurb4 = itnFieldCleanup(
            row['altblurb4'], qutation=True, styling=True) if row['altblurb4'] is not "" else ""

        cleaned.append({"year": row['year'], "time": row['time'], "itn_header": header,
                        "article": article, "article2": article2, "blurb": blurb, "altblurb": altblurb,
                        "altblurb2": altblurb2, "altblurb3": altblurb3, "altblurb4": altblurb4})

        utl.writeRowsCSV(cleaned, fieldnames=["year", "time", "itn_header", "article", "article2", "blurb",
                                              "altblurb", "altblurb2", "altblurb3", "altblurb4"], filenames='blurb_itn.csv')


# blurbCollecting("itns.csv")
