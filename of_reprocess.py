# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 03:25:51 2023

@author: dwgre
"""

import os
import json
import logging
import scraper
from colorama import Fore
from datetime import datetime

INTERVAL = 20

def set_logging():
    logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s.%(funcName)s %(message)s',
                        datefmt='%Y%m%d %H:%M:%S',
                        filename=f'{scraper.get_home()}/logs/only_reprocess.log',
                        level=logging.INFO,
                        encoding='utf-8')
    _logging = logging.getLogger(__name__)
    scraper.add_stderr_logging()

def read_log():
    with open(f"{scraper.get_home()}/last_o") as fp:
        return sorted(set(_x for _x in fp.read().split("\n") if _x))


def write_log(users):
    with open(f"{scraper.get_home()}/last_o", "a") as fp:
        return fp.write("\n".join(users) + "\n")

def __write(payload):
    _payload = {_k: _v for _k, _v in payload.items() if _v}
    _filename = f'{scraper.get_home()}/finals/onlyfinder-{datetime.now().strftime("%Y%m%dT%H%M%S")}-final.json'
    with open(_filename, 'w') as _fp:
        json.dump(_payload, _fp, indent=4)
    logging.info('Wrote %s to %s', len(_payload), _filename)
    write_log(sorted(payload.keys()))


if __name__ == "__main__":
    set_logging()

    _fg = {}
    files = {}
    for _f in sorted(os.listdir(f'{scraper.get_home()}/onlyfinder')):
        if _f in files:
            continue
        files[_f] = 1
        filename = f'{scraper.get_home()}/onlyfinder/{_f}'
        print(_f)
        with open(filename) as fp:
            _fg.update(json.load(fp))
    with open(f"{scraper.get_home()}/of0.json") as fp: 
        of0 = json.load(fp)

    newOnes = sorted([_x for _x in (set(_fg) - set(of0)) if 'fansly:' not in _x])
    newPayload = {}
    newOnes = sorted(set(newOnes) - set(read_log()))
    logging.info("%s entries, starting from %s", len(newOnes), newOnes[0])

    driver = scraper.get_driver('chrome')
    for index, user in enumerate(newOnes, start=1):
        _data = scraper.info(driver, user)
        newPayload[user] = {}
        if _data:
            newPayload[user].update(_fg[user])
            newPayload[user].update(_data)
        if index % INTERVAL == 0 or index >= len(newOnes):
            __write(newPayload)
            newPayload = {}
