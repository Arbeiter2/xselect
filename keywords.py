# -*- coding: utf-8 -*-
"""
Created on Sat Jun 18 06:32:43 2022

@author: dwgre
"""
import re
from nltk.util import ngrams
from nltk.corpus import stopwords
from scraper import strip_disclaimer
import ontology

STOPS = set()
for lang in ['dutch', 'english', 'finnish', 'french', 'german', 'greek', 'hungarian', 'italian', 'portuguese', 'romanian', 'russian', 'spanish', 'swedish', ]:
    STOPS = STOPS.union(set(stopwords.words(lang)))

WHITESPACE = re.compile(r'\s+')
WORD_CHARS = re.compile(r'[^\w\s]+', re.UNICODE)
SENTENCES = re.compile(r'[\n\.]+')
AGE = re.compile(r'\D+(\d{2})\s*(ans|anos|anni|jahre|years?|yrs?|a\u00f1os)')
AGE2 = re.compile(r'I[\'’]m (\d{2})')
HEIGHT_CM = re.compile(r'(\d{3})\s?(cms?)')
HEIGHT_M = re.compile(r'(\d\.\d+)\s?(m|metres?)')
HEIGHT_FT = re.compile(r'(\d(\.\d+)?)\s?(ft|feet|foot)\W')
HEIGHT_FT_IN = re.compile(r'(\d)\s?(ft|feet|foot|’|\')[ ]?(\d{1,2})(\s?(in|inch|inches|\"))?')
VERGON_CM = re.compile(r'(\d+(\.\d+)?)\s?(cms?) (dick|cock)')
VERGON_IN = re.compile(r'(\d+(\.\d+)?)\s?(ins?|inch|inches|\") (dick|cock)')

def shingler(text: str, n: int=2):
    sentences = [_t.strip() for _t in SENTENCES.split(text.lower()) if _t]
    output = []
    for _s in sentences: 
        _s = WORD_CHARS.sub(' ', _s)
        tokens = [token for token in WHITESPACE.split(_s) if token != ""]
        slices = list(ngrams(tokens, n))
        output.append([' '.join(_s) 
                       for _s in slices if len(set(_s) & STOPS) == 0])
    return sum(output, [])


def build_keywords(of0):
    user_keywords = {}
    for k_len in range(1, 4):
        user_keywords[k_len]= {
            _u: shingler(strip_disclaimer(_d['description']), k_len)
            for _u, _d in of0.items() if 'description' in _d
        }
    keyword_users = {}
    for k_len, _keys in user_keywords.items():
        for _u, _k in _keys.items():
            for _s in _k:
                _q = keyword_users.get(_s, set())
                _q.add(_u)
                keyword_users[_s] = _q
    return {_k: list(_u) for _k, _u in keyword_users.items()}

def build_keywords_n(text, n=1):
    out = []
    if n < 1:
        n = 1
    for k_len in range(1, n+1):
        for word in shingler(strip_disclaimer(text), k_len):
            out = out + ontology.getTags(word)
    return sorted(list(set(out)))

def __to_mm(**kwargs) -> float:
    mm = 0
    if 'cm' in kwargs:
        mm = 10.0 * int(kwargs['cm'])
    elif 'm' in kwargs:
        mm = 1000.0 * float(kwargs['m'])
    elif 'feet' in kwargs:
        mm = 304.8 * float(kwargs['feet'])
    if 'inches' in kwargs:
        mm += 25.4 * float(kwargs['inches'])
    return mm

def vergon(description: str):
    vergon_= {}
    _m = VERGON_CM.search(description)
    if _m:
        vergon_['cm'] = _m.group(1)
    else:
        _m = VERGON_IN.search(description)
        if _m:
            vergon_['inches'] = _m.group(1)
    return __to_mm(**vergon_)

def height(description: str):
    height_= {}
    _m = HEIGHT_M.search(description)
    if _m:
        #print(f"{entry['account']} HEIGHT: {_m.group(1)} m")
        height_['m'] = _m.group(1)
    else:
        _m = HEIGHT_CM.search(description)
        if _m:
            #print(f"{entry['account']} HEIGHT: {_m.group(1)} cm")
            height_['cm'] = _m.group(1)
        else:
            _m = HEIGHT_FT_IN.search(description)
            if _m:
                #print(f"{entry['account']} HEIGHT: {_m.group(1)} feet {_m.group(3)} inches")
                height_['feet'] = _m.group(1)
                height_['inches'] = _m.group(3)
            else:
                _m = HEIGHT_FT.search(description)
                if _m:
                    #print(f"{entry['account']} HEIGHT: {_m.group(1)} feet")
                    height_['feet'] = _m.group(1)    
    return __to_mm(**height_)


def age(description: str):
    _m = AGE.search(description)
    if _m:
        return int(_m.group(1))
    _m = AGE2.search(description)
    if _m:
        return int(_m.group(2))
    return 0

def detect(entry):
    _m = AGE.search(entry['description'])
    if _m:
        print(f"{entry['account']} AGE: {_m.group(1)}")
    height_= height(entry['description'])
    if height_:
        print(f"{entry['account']} HEIGHT: {int(height_/10)} cm")
    vergon_= vergon(entry['description'])
    if vergon_:
        print(f"{entry['account']} VERGON: {int(vergon_/10)} cm")

def reload():
    ontology.reload()
