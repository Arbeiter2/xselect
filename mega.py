# -*- coding: utf-8 -*-
"""
Created on Mon Jan  3 19:06:28 2022

@author: dwgre
"""
from collections import OrderedDict
import json
from selenium.common.exceptions import WebDriverException
import scraper

with open('/home/delano/proj/xselect/xz.json') as fp:
    vv = json.load(fp)
with open('/home/delano/super.txt') as fp:
    mega = fp.read().split("\n")
    
ml = sorted(set(mega) - set(vv))
ml = [_x for _x in ml if _x]

driver = scraper.get_driver()
_latest = {}
for _u in ml:
    try:
        _l = scraper.info(driver, _u)
        if _l:
            _latest[_u] = _l
    except WebDriverException:
        driver = scraper.get_driver()
        print("-- Forcing driver restart")
vv.update(_latest)
_latest = OrderedDict({_x: vv[_x] for _x in sorted(vv)})
with open('/home/delano/super.json', 'w') as fp:
    json.dump(_latest, fp, indent=4)
