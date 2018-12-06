#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 12:58:16 2018


grap location from info box:

    parsing info box to get the location
    https://github.com/siznax/wptools/wiki

@author: angli
"""
import pandas as pd
#import urllib
#import infoboxGrabbing as wpinfo
import wptools
import pickle
import re


def checkLocKeys(key_lst_lower):
    checkstrlst = ['site', 'coordinate','map', 'place','capital', 'city', 'country']
    outlockeys_lower = []
    for key in key_lst_lower:
        for chsckstr in checkstrlst:
            if chsckstr in key:
                outlockeys_lower.append(key)
    return outlockeys_lower



def locInfobox(data):
    loc_info_data = {}
    
    i=0
    for index, row in data.iterrows():
        i+=1
        if i%50 == 0: print (i)
        postid = row['postid']
        
        #first level key: postid
        loc_info_data[postid] = {}
        
        #second level keys: en_title, info_location, info_relates
        pagetitle = str(row["en_title"])
        loc_info_data[postid]["en_title"] = pagetitle
        
        page = wptools.page(pagetitle)#info box
        page.get_parse()
        infocontent = page.data.get('infobox')
        
        loc_info_data[postid]['country_code'] = ""
        loc_info_data[postid]['country'] = ""
        loc_info_data[postid]['residence'] = ""
        loc_info_data[postid]["info_location"] = [None,None,None]
        loc_info_data[postid]["info_relates"] = []
        if infocontent is not None:
            key_lst = list(infocontent.keys())
            key_lst_lower = [x.lower() for x in key_lst]
            checked_keys = []
            if "location" in key_lst_lower:
                x = key_lst[key_lst_lower.index("location")]
                checked_keys.append(x)
                loc_info_data[postid]["info_location"][0] = infocontent.get(x)
            if "locale" in key_lst:
                y = key_lst[key_lst_lower.index("locale")]
                checked_keys.append(y)
                loc_info_data[postid]["info_location"][1] = infocontent.get(y)
            if "nationality" in key_lst:
                z = key_lst[key_lst_lower.index("nationality")]
                checked_keys.append(z)
                loc_info_data[postid]["info_location"][2] = infocontent.get(z)
            if "country_code" in key_lst:
                a = key_lst[key_lst_lower.index("country_code")]
                checked_keys.append(a)
                loc_info_data[postid]["country_code"] = infocontent.get(a)
            if "country" in key_lst:
                b = key_lst[key_lst_lower.index("country")]
                checked_keys.append(b)
                loc_info_data[postid]["country"] = infocontent.get(b)
            if "residence" in key_lst:
                c = key_lst[key_lst_lower.index("residence")]
                checked_keys.append(c)
                loc_info_data[postid]["residence"] = infocontent.get(c)
            
            other_lockeys_lower = checkLocKeys(key_lst_lower)
            if len(other_lockeys_lower) != 0:
                for lockey_lower in other_lockeys_lower:
                    lockey = key_lst[key_lst_lower.index(lockey_lower)]
                    loc_item = infocontent.get(lockey)
                    loc_info_data[postid]["info_relates"].append(loc_item)
    
    return loc_info_data


def city_country_gnrtor():
    """
    this is to return a country_code:[cities] dictionary for check
    """
    column_names = ["geonameid", "name", "asciiname", "alternatenames", "lati", "longti", "featureclasee", "featurecode","country_code","cc2","admin1code","admin2code","admin3code","admin4code","population","elevation","dem","timezone","modifieddate"]
    citi500_country = pd.read_table("/Users/angli/ANG/OneDrive/Documents/Pitt_PhD/ResearchProjects/datasets/cities500.txt", header=None, names = column_names)
    
    country_grouped = citi500_country.groupby("country_code")
    country_cities = {}
    n=0
    for cgroup in country_grouped:
        n+=1
        #if n==1: break
        country_code = cgroup[0]
        
        #select on before and after
        country_data = cgroup[1]#.groupby(['after_first_event_edit']) 
        cities1 = list(country_data['name'].dropna())
        cities2 = list(country_data['asciiname'].dropna())
        cities3 = list(country_data['alternatenames'].dropna())
        cities = []
        for alternames in cities3:
            altername_lst = alternames.split(",") 
            cities = cities + altername_lst
        cities = list(set(cities + cities1 + cities2))
        cities_lst = [x for x in cities if x is not None]
        country_cities[country_code] = cities_lst
    
    return country_cities
    



def countryInfo():
    colnames = ["ISO", "ISO3", "ISONum", "fips", "Country", "Capital", "Area","Population", "Countinent", "tld", "currencycode","CurrencyName","Phone","PostalCodeFormat","PostalCodeRegex","Languages","geonameid","neighbours","EquivalentFipsCode"]
    contryinfo = pd.read_table("/Users/angli/ANG/OneDrive/Documents/Pitt_PhD/ResearchProjects/datasets/countryinfo_data.txt",  index_col=False, names = colnames)
    #len(list(set(list(contryinfo['Country']))))
    country_lst = []
    country_code_dict = {}
    country_langs_dict = {}
    for ind, row in contryinfo.iterrows():
        country_code = row["ISO"]
        country = row['Country'].lower()
        language = row['Languages']
        #neighbours = row['neighbours']
        country_lst.append(country)
        country_code_dict[country] = country_code
        country_langs_dict[country_code] = language
    return (country_lst, country_code_dict, country_langs_dict)

    
def locProcess(loc_info_data):
    URL_PATTERN=re.compile(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')
    loc_clean_terms = {}
    for postid, content in loc_info_data.items():
        locationTerms = [None, None, None] # country_code, country, residence
        otherTerms = []
        if content.get("country_code") is not None:
            country_code_raw = content.get("country_code")
            country_code_raw = re.sub(URL_PATTERN, '', country_code_raw)
            country_code = re.sub(r'[^a-zA-Z]', ' ',country_code_raw)
            country_code = country_code.strip()
            locationTerms[0] = country_code.upper()
        if content.get("country") is not None:
            country_raw = content.get("country")
            country_raw = re.sub(URL_PATTERN, '', country_raw)
            country = re.sub(r'[^a-zA-Z\-\_]', ' ',country_raw)
            country_lst = country.lower().strip().split(" ")
            country_lst_clean = [x for x in country_lst if x != ""]
            country_clean = " ".join(country_lst_clean)
            locationTerms[1] = country_clean
        if content.get("residence") is not None:
            residence_raw = content.get("residence")
            residence_raw = re.sub(URL_PATTERN, '', residence_raw)
            residence = re.sub(r'[^a-zA-Z\-\_\']', ' ',residence_raw)
            residence_lst = residence.lower().strip().split(" ")
            residence_lst_clean = [x for x in residence_lst if x != ""]
            residence_clean = " ".join(residence_lst_clean)
            locationTerms[2] = residence
        if list(set(content["info_location"]))[0] is not None:
            #rawterms = list(set(content["info_location"]))
            rawterms = [x for x in list(set(content["info_location"])) if x is not None]
            rawterms = [re.sub(URL_PATTERN, '', x) for x in rawterms]
            term = [re.sub(r'[^a-zA-Z\-\_]', ' ', x) for x in rawterms]
            otherTerms += term
        if content.get("info_relates") is not None:
            info_raw_lst = content.get("info_relates")
            info_raw_lst = [re.sub(URL_PATTERN, '', x) for x in info_raw_lst]
            info_lst = [re.sub(r'[^a-zA-Z\-\_]', ' ', x) for x in info_raw_lst]
            otherTerms += info_lst
        
        loc_clean_terms[postid] = [content['en_title'], locationTerms, otherTerms]
    
    return loc_clean_terms
    


def checkCountryfromCity(term, country_citi_dict):
    #this is to check: given terms, whether it includes city term, and retrieve the country code 
    yes_country = []
    possible_country = []
    for country_code, city_lst in country_citi_dict.items():
        for city in city_lst:
            if city.lower() == term.lower(): #or (term.lower() in city.lower()):
                yes_country.append(country_code)
            elif (city.lower() in term.lower()) or (term.lower() in city.lower()):
                possible_country.append(country_code)
    return  (yes_country, possible_country)
    

def checkCountryfromCountry(term, country_lst, country_code_dict):
    #this is to check: given terms, whether it includes country term, and retrieve the country code 
    yes_country = []
    possible_country = []
    for country in list(country_code_dict.keys()):
        if country.lower() == term.lower():
            yes_country.append(country_code_dict[country])
        elif (country.lower() in term.lower()) or (term.lower() in country.lower()):
            possible_country.append(country_code_dict[country])
    return (yes_country, possible_country)



if __name__ == "__main__":
    data = pd.read_csv("/Users/jiajunluo/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/post_articles_set_r1.csv")
    
    #raw location related info from infobox
    loc_info_data = locInfobox(data)
    #pickle.dump( loc_info_data, open( "/Users/jiajunluo/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/post_loc_info.p", "wb" ) )
    #loc_info_data = pickle.load( open( "/Users/angli/ANG/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/post_loc_info.p", "rb" ) )
    
    #cleaned loc info from processed loc_info_data
    loc_clean_terms = locProcess(loc_info_data)
    
    #country info needed to be matched
    country_citi_dict = city_country_gnrtor() #country:[all posible city names]
    
    #pickle.dump( country_citi_dict, open( "/Users/angli/ANG/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/country_citi_dict.p", "wb" ) )
    #country_citi_dict = pickle.load( open( "/Users/angli/ANG/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/country_citi_dict.p", "rb" ) )
    country_lst, country_code_dict, country_langs_dict = countryInfo() #country names as key
    
    for postid, item in loc_clean_terms.items():
        en_title = item[0]
        yes_countries = []
        possible1_countries = []
        possible2_countries = []
        
        locationTerm_lst = [x for x in item[1] if x != ""]
        otherTerms_lst = item[2]

        if len(locationTerm_lst) != 0:
            for locterm in locationTerm_lst:
                yes_citicheck, possibles_citicheck = checkCountryfromCity(locterm, country_citi_dict)
                yes_countries.append(yes_citicheck)
                yes_countrycheck, possible_countrycheck = checkCountryfromCountry(locterm, country_lst, country_code_dict)
                .append( + yes_countrycheck
        if len(otherTerms_lst) != 0:
            for oterm in otherTerms_lst:
                yes_citicheck, possibles_citicheck = checkCountryfromCity(oterm, country_citi_dict)
                yes_countrycheck, possible_countrycheck = checkCountryfromCountry(oterm, country_lst, country_code_dict)
                yes_countries = yes_countries + yes_citicheck + yes_countrycheck
                
            
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
