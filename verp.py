# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 08:31:21 2022

@author: dwgre
"""
import logging
import json
from datetime import datetime
import twitter

logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s.%(funcName)s %(message)s',
                    datefmt='%Y%m%d %H:%M:%S',
                    filename=f'{twitter.scraper.get_home()}/logs/reprocess.log',
                    level=logging.INFO)
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler())
LAST_OF = f'{twitter.scraper.get_home()}/last_of'
LAST_URL = f'{twitter.scraper.get_home()}/last_url'

def get_last(filename):
    try:
        with open(filename) as fp:
            last = fp.read()
        return last
    except Exception:
        return None
 
def put_last(filename, value):
    with open(filename, 'w') as fp:
        fp.write(value)


def get_all_onlyfan_from_lists(driver: twitter.webdriver, url_list: list) -> list:
    _x = set()
    last_url = get_last(LAST_URL)
    if last_url:
        _i = url_list.index(last_url)
        url_list = url_list[_i:]
        LOGGER.info("Starting at location %s (%s)", _i, last_url)
        
    for _u in url_list:
        put_last(LAST_URL, _u)
        _tw = twitter.ONLYFANS_URL.search(_u)
        if _tw:
            LOGGER.info(_tw.string)
            _tw = [_tw.group(1).lower()]
        elif twitter.LINKTREE_URL.search(_u):
            _tw = twitter.get_linktree_onlyfans(driver, _u)
        elif twitter.GETSLINK_URL.search(_u):
            _tw = twitter.get_getslink_onlyfans(driver, _u)
        elif twitter.MYSLINK_URL.search(_u):
            _tw = twitter.get_getslink_onlyfans(driver, _u)
        else:
            _tw = []
            for _s, _p in twitter.LINK_SITES.items():
                if not _p.search(_u):
                    continue
                _twl = twitter.get_link_onlyfans(driver, _u)
                if _twl:
                    _twl = list(set(_twl))
                    LOGGER.info('%s (%s)', _twl, _s)
                    _tw.extend(_twl)
        if _tw:
            _x.update(set(_tw))
    return list(_x)


def main():
    with open(f'{twitter.scraper.get_home()}/xcept') as fp:
        xpt2 = [_x for _x in fp.read().split('\n') if _x]
    driver = twitter.scraper.get_driver('firefox')
    onlyfans_links = get_all_onlyfan_from_lists(driver, xpt2)
    cds = {}
    last = get_last(LAST_OF)
    if last:
        _i = onlyfans_links.index(last)
        onlyfans_links = onlyfans_links[_i:]
        LOGGER.info("Starting at location %s (%s)", _i, last)

    for _u in onlyfans_links:
        cds[_u] = twitter.scraper.info(driver, _u)
        put_last(LAST_OF, _u)
    vw = {_u: cds[_u] for _u in sorted(cds) if cds[_u]}
    _filename = f'{twitter.scraper.get_home()}/finals/reprocess-{datetime.now().strftime("%Y%m%dT%H%M%S")}.json'
    with open(_filename, 'w') as fp:
        json.dump(vw, fp, indent=4)
    LOGGER.info('Successfully wrote %s to %s', len(vw), _filename)

if __name__ == '__main__':
    main()
