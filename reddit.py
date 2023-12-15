# -*- coding: utf-8 -*-
"""
Created on Sun Apr 17 17:29:41 2022

@author: dwgre
"""
import time
from datetime import datetime
import json
import re
import logging
import requests
import scraper

GAY_ONLYFANS = [
    'amateurgayporn',
    'amateurgirlsbigcocks',
    'asiangirls4whitecocks',
    'asiangirlsblackcocks',
    'barebackgayporn',
    'bestofgayonlyfans',
    'bigblackcocks',
    'bigcock1234',
    'bigcockchurch',
    'blackcocks',
    'buymaleonlyfans',
    'cockappreciations',
    'cockcuddling',
    'cocklust',
    'cockmilking',
    'cocksandsocks',
    'cocksinla',
    'cumcovereddeepthroat',
    'cumcoveredsluts',
    'gayblowjobs',
    'gaybreeding',
    'gaybrosgonewild',
    'gaycocksuckers',
    'gaycouplesgonewild',
    'gaycumhaters',
    'gaycumsluts',
    'gayfootfetish',
    'gayjock',
    'gaykink',
    'gaymuscleworship',
    'gayonlyfans',
    'gayonlyfansaccount',
    'gayonlyfansautopromo',
    'gayonlyfansbeginners',
    'gayonlyfanslatino',
    'gayonlyfanspromo',
    'gayonlyfanspromotions',
    'gayonlyfansreview',
    'gayonlyfansreviews',
    'gayonlyfansscams',
    'gayporn',
    'gaysofonlyfans',
    'gothjock',
    'guysinsweatpants',
    'handsfreecum',
    'horsecocksmasterrace',
    'hotjocks',
    'hungryforcock',
    'imalexxonlyfans',
    'imcravingcock',
    'jockfeet',
    'jockstraps',
    'jockwatch',
    'maleonlyfans',
    'maleonlyfriends',
    'malesexworkersonly',
    'massivecock',
    'massivecockvids',
    'monstercock',
    'monstercockmadness',
    'monstercocks',
    'muscleworship',
    'nsfw_gay',
    'nsfw_gays',
    'onceyougoblackcock',
    'onlyfan_gay',
    'onlyfans_gay_tv',
    'onlyfans_males',
    'onlyfansaussie_gay',
    'onlyfansbutgay',
    'onlyfanscumsluts',
    'onlyfansformales',
    'onlyfansgatheredgay',
    'onlyfansgaycouples',
    'onlyfansgays',
    'onlyfansmalemodels',
    'onlyfansmalestartup',
    'ratemycock',
    'sharegayonlyfans',
    'whitegirlsasiancocks',
    'whitesocksjocks',
    'world_of_cum',
    'younghungfullofcum'
]
REDDIT_USER_XPATH = '//a[contains(@href, "/user/")]'
REDDIT_URL_RE = re.compile(r'\/user\/(\w+)')
REDDIT_COMMENT_XPATH = '//a[contains(@href, "/comments/")]'
REDDIT_COMMENT_RE = re.compile(r'\/comments\/([a-zA-Z0-9]+)\/[^\/]+')

logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s.%(funcName)s %(message)s',
                   datefmt='%Y%m%d %H:%M:%S',
                   filename=f'{scraper.get_home()}/logs/reddit.log',
                   level=logging.INFO)
LOGGER = logging.getLogger(__name__)
scraper.add_stderr_logging()

#LOGGER.addHandler(logging.StreamHandler())

def __get_onlyfans_accounts(r_, users):
    """
    Get dictionary of author data
    """
    init_len = len(users)
    for post in r_['data']['children']:
        if post["data"]["author"] in users:
            #LOGGER.info(f'[{post["data"]["author"]}]')
            continue
        url = f'https://www.reddit.com/user/{post["data"]["author"]}/comments.json'
        _c = requests.get(url, headers=scraper.HEADERS)
        if _c.status_code != 200:
            continue
        _c = _c.json()
        found = False
        if 'data' not in _c:
            continue
        for _cl in _c['data']['children']:
            for field in ['link_title', 'body']:
                if not found:
                    _m = scraper.ONLYFANS_USER_RE.findall(_cl['data'][field])
                    if _m:
                        users[post["data"]["author"]] = (
                            set.union(users.get(post["data"]["author"], set()),
                                      {_x.lower() for _x in _m})
                        )
                        LOGGER.info('%s -> %s', post["data"]["author"],
                                    list(users[post["data"]["author"]]))
                        found = True
            if found:
                break
        time.sleep(0.01)
    if len(users) == init_len:
        LOGGER.info("No users added")
    return users


def get_reddit(subreddit: str, listing: str ='new', limit: int =100, **kwargs) -> dict:
    """
    :param: subreddit : str
    :param: listing : str, optional
    :param: limit : int, optional
    :param: **kwargs : TYPE
    """
    timeframe = kwargs.get('timeframe', 'all')
    after = kwargs.get('after', None)
    try:
        base_url = f'https://www.reddit.com/r/{subreddit}/{listing}.json?limit={limit}&t={timeframe}'
        if after:
            base_url = base_url + f"&after={after}"
        request = requests.get(base_url, headers=scraper.HEADERS)
    except:
        LOGGER.error('An Error Occurred')
        return {}
    try:
        js_ = request.json()
        return js_
    except json.decoder.JSONDecodeError:
        LOGGER.error(request.text)
        return {}


def get_onlyfans_from_reddit(subreddit: str, users: dict) -> list:
    """
    Find all onlyfans accounts from subreddit. Stop iterating through pages after
    two (2) pages with no results.

    Args:
        subreddit (str): [description]

    Returns:
        list: [description]
    """
    after = None
    #for i in range(0, 10):
    last = 0
    i = 0
    while True:
        i = i + 1
        LOGGER.info("%s/%s", subreddit, i)
        r_ = get_reddit(subreddit, after=after)
        if 'error' in r_:
            LOGGER.error('Error reading subreddit %s: %s', 
                         subreddit, r_['error'])
            return {}
        current_length = len(users)
        users.update(__get_onlyfans_accounts(r_, users))
        if len(users) == current_length:
            last = last + 1
            if last == 2:
                break
        after = r_['data']['after']
        time.sleep(0.5)
    return users



def mega(current: dict =None) -> dict:
    users = {}
    for subreddit in GAY_ONLYFANS:
        get_onlyfans_from_reddit(subreddit, users)
    out = {}
    driver = scraper.get_driver('chrome')
    complete = set()
    for _k in users.values():
        complete = complete|_k
    for _k in sorted(complete & set(current.keys())):
        _i = scraper.info(driver, _k)
        if _i:
            out[_k] = _i
    driver.close()
    driver.quit()
    return out

def main():
    path = f'{scraper.get_home()}/of0.json'
    with open(path) as fp_:
        b_0 = json.load(fp_)
    b_1 = mega(b_0)
    #b_1.update(b_0)
    outfile = f'{scraper.get_home()}/finals/redditors-{datetime.now().strftime("%Y%m%dT%H%M%S")}.json'
    with open(outfile, 'w') as fp_:
        json.dump(b_1, fp_, indent=4)
    LOGGER.info('Successfully wrote %s to %s', len(b_1), outfile)


if __name__ == "__main__":
    main()
