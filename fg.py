# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 20:51:38 2022

@author: dwgre
"""
import os
import json
import re
import requests

FILENAME = re.compile(r'\/([0-9a-zA-Z\-_]+\.\w+)\?')


def process(path: str, entry: dict):
    entry['filenames'] = {}
    comment = f' - {entry["title"]}' if entry["title"] else ""
    for idx, _u in enumerate(entry['urls'], 1):
        raw_filename = FILENAME.search(_u).group(1)
        if not comment:
            download_filename = f'{entry["date"]}-{raw_filename}'
        elif len(entry['urls']) > 1:
            download_filename = f'{entry["date"]}{comment} - {idx}.{(raw_filename.split("."))[1]}' 
        else:
            download_filename = f'{entry["date"]}{comment}.{(raw_filename.split("."))[1]}' 
        entry['filenames'][raw_filename] = download_filename
        print(f"[{raw_filename}] -> [{download_filename}]")
        resp = requests.get(_u)
        with open(f"{path}/{download_filename}", "wb") as f:
            f.write(resp.content)

_fg = {}
for _f in sorted(os.listdir('H:/finals')):
    filename = f'H:/finals/{_f}'
    print(filename)
    with open(filename) as fp:
        _fg.update(json.load(fp))


