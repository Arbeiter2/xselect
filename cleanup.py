# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 15:48:49 2022

@author: dwgre
"""
import  sys
import re
import logging
import face_gender.predict_gender as gender


def get_home():
    if sys.platform != 'win32':
        return '/home/delano'
    return 'H:'

logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s.%(funcName)s %(message)s',
                   datefmt='%Y%m%d %H:%M:%S',
                   filename=f'{get_home()}/logs/gender_guess.log',
                   level=logging.INFO)
LOGGER = logging.getLogger(__name__)

GIRLS = None
BOYS = None
SCORE_THRESHOLD = 0.75

for _file in ('girls', 'boys'):
    with open(f'./{_file}.txt') as _fp:
        _gl = [_g for _g in _fp.read().split('\n') if _g]
        _gl = sorted(_gl, key=lambda x: (-len(x), x))
    globals()[_file.upper()] = re.compile(f"({'|'.join(_gl)})")


def candidates(users: dict) -> dict:
    out = {}
    for _n, data in users.items():
        if 'avatar' not in data:
            continue
        out[_n] = {}
        out[_n]['name'] = super_search(_n)
        img = gender.load_image(data['avatar'])
        out[_n]['avatar'] = gender.predict(img)
        _guess = guess(out[_n])
        out[_n]['guess'] = list(set(_guess.values()) - {None})
        LOGGER.info("account='%s', guess=%s", _n, out[_n]['guess'])
    return out

def super_search(target: str) -> list:
    out = {}
    for _p, _k in zip((GIRLS, BOYS), ('Female', 'Male')):
        out[_k] = sorted(set(_p.findall(target)), key=len, reverse=True)
    return out

def guess(entry: dict) -> str:
    out = {}
    out['name'] = __guess_from_name(entry)
    out['avatar'] = __guess_from_avatar(entry)
    return out
    
def __guess_from_name(entry: dict):
    names = {}
    common = set(entry['name']['Female']) & set(entry['name']['Male'])
    for _g in ('Female', 'Male'):
        names[_g] = sorted(set(entry['name'][_g]) - common, key=len,
                           reverse=True)
    name_gender = None
    if len(names['Male']) == 0 and len(names['Female']) == 0:
        return None
    elif len(names['Male']) == 0 and len(names['Female']) > 0:
        name_gender = 'Female'
    elif len(names['Male']) > 0 and len(names['Female']) == 0:
        name_gender = 'Male'
    elif len(names['Female'][0]) > len(names['Male'][0]):
        name_gender = 'Female'
    elif len(names['Female'][0]) < len(names['Male'][0]):
        name_gender = 'Male'
    return name_gender

def __guess_from_avatar(entry: dict):
    if ('faces' not in entry['avatar']) or not entry['avatar']['faces']:
        return None
    best = sorted(entry['avatar']['faces'], key=lambda x: x['score'],
                  reverse=True)[0]
    if best['score'] >= SCORE_THRESHOLD:
        return best['gender']
    return None
