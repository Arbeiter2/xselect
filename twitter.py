# -*- coding: utf-8 -*-
"""
Created on Sat Dec 25 21:37:12 2021

@author: dwgreenidge
"""
import logging
import time
from datetime import datetime
import re
import argparse
import json
from collections import OrderedDict
import html
from urllib.parse import unquote, urlencode
from urllib3.exceptions import ProtocolError
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException,\
     WebDriverException, ElementClickInterceptedException, NoSuchWindowException,\
     StaleElementReferenceException

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import scraper

LOGGER = logging.getLogger(__name__)
# logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s.%(funcName)s %(message)s',
#                     datefmt='%Y%m%d %H:%M:%S',
#                     filename=f'{scraper.get_home()}/logs/scraper.log',
#                     level=logging.INFO)
BEARER_TOKEN = (
                'AAAAAAAAAAAAAAAAAAAAABwWWQEAAAAAk1xgeuk0JBijGO5cQJV8pDKwKGg%3DU'
                'pvfZ8t9bEUo3gQlA8qbtnisqGTngn95pXBxPAomGFxFPEd1qm',

                'AAAAAAAAAAAAAAAAAAAAAGwfgAEAAAAAnCjPvtybXeXyQLE9brxI8lyhhJM%3Dz'
                'PtpsjKdbCEfEzwjQhmyAXqEsefE6SQ4AkS1YUEde5TbmhxP1k',

                'AAAAAAAAAAAAAAAAAAAAANkWfQEAAAAA0sTXKl3cq0X7CWxV31XOUaYpwsM%3D'
                'nyrWJ4pHR3T8BjBzsNsC45pgWMhZO8iIwTRHwDxmrdmOhrmPLL')
LINKTREE_ONLYFANS = ('//p[contains(translate(., "ABCDEFGHIJKLMNOPQRSTUVWXYZ", '
                     '"abcdefghijklmnopqrstuvwxyz"), "only fans")]/../../..')
LINKTREE_ONLYFANS1 = ('//p[contains(translate(., "ABCDEFGHIJKLMNOPQRSTUVWXYZ", '
                     '"abcdefghijklmnopqrstuvwxyz"), "onlyfans")]/../../..')
LINKTREE_ONLYFANS2 = 'button[type="ONLYFANS"] > p'
MYBIO_URL = re.compile(r'my\.bio\/([a-zA-Z0-9_\-\.]+)', re.IGNORECASE)
ONLYFANS_URL = re.compile(r'onlyfans.com\/([a-zA-Z0-9_\-\.]+)\/?',
                          re.IGNORECASE)
JUSTFANS_URL = re.compile(r'justfor.fans\/([a-zA-Z0-9_\-\.]+)', re.IGNORECASE)
ANY_URL = re.compile(r'https:\/\/\w+(?:\.\w+)+(?:\/[a-zA-Z0-9_\-%\+=\?@#~,.\$&]+)+')
LINKTREE_URL = re.compile(r'linktr\.ee\/([a-zA-Z0-9_\-.]+)', re.IGNORECASE)
GETSLINK_URL = re.compile(r'getsl\.ink', re.IGNORECASE)
MYSLINK_URL = re.compile(r'myslink\.app', re.IGNORECASE)
ALLMYLINKS_CARD = re.compile(r'allmylinks.com\/profile\/business-card-download.+type=jpeg', re.IGNORECASE)
ALLMYLINKS_QR = re.compile(r'allmylinks.com\/profile\/qr\?id=\d+', re.IGNORECASE)
LINK_SITES = {
    _s: re.compile(_s.replace('.', '\\.'), re.IGNORECASE)
    for _s in [#'allmylinks.com', 
               'instabio.cc', 'lnk.bio', 'my.bio', 'linkfly.to']
}
LINKR_URL = re.compile(r'linkr\.bio\/([a-zA-Z0-9_\-.]+)', re.IGNORECASE)

USER_FIELDS = 'url,description,public_metrics,entities'
PAGINATION = re.compile(r'pagination_token=(\w+)')
FEM = re.compile(r'(b[0o]{2}bs?|tits?|b[0o]{2}ty|babe|baby|sweet|sugar|girl|honey|girl|ch[i1]ck|p.ssy)$')
MEF = re.compile(r'(br[o0]s?|guy|man|cub|pig|prince|daddy|dilf|adonis|king|wolf|b[o0][iy]|beast|muscle|j[o0]ck|prince|master|cock|d[i1]ck|schwanz|schlong|dude|stud|femboy|tw[ui]nk|bear|xl|cabron|papi|macho|b[cw]c|cholo)')
linktree_available = True
twitter_acct = None

def create_headers(app_id: int=0):
    """
    Create dictionary of headers for use with requests.get
    """
    headers = {"Authorization": f"Bearer {BEARER_TOKEN[app_id]}"}
    return headers


def get_user(user_id: str, app_id=0) -> str:
    """
    Get twitter user object for a twitter handle or numeric ID
    """
    if re.match(r'\d+$', user_id.strip()):
        lookup = ''
    else:
        lookup = '/by/username'
    url = (f'https://api.twitter.com/2/users{lookup}/{user_id.strip()}/?'
           f'user.fields={USER_FIELDS}')
    #print(url)
    try:
        req = requests.get(url, headers=create_headers(app_id))
        _r = req.json()
    except json.decoder.JSONDecodeError:
        LOGGER.error("user_id: [%s], URL: %s, Status code: %s, Reason: %s", user_id,
                     url, req.status_code, req.reason)
        raise
    LOGGER.info("version = %s\n%s", app_id, json.dumps(_r, indent=4))
    if 'data' not in _r:
        #print(_r)
        return None
    return _r['data']



def __get_next_page(twitter_url: str, token: str =None, app_id: int=0):
    if token:
        _m = PAGINATION.search(twitter_url)
        if 'pagination_token=' in twitter_url:
            twitter_url = twitter_url.replace(_m.group(1), token)
        else:
            twitter_url += f'&pagination_token={token}'
    return requests.get(twitter_url, headers=create_headers(app_id))


def __paginator(url: str, app_id: int=0):
    out = []
    token = None
    sleep_time = 65
    while True:
        response = __get_next_page(url, token, app_id)
        if response.status_code != 200:
            LOGGER.error('[%s] %s', response.status_code, response.reason)
            LOGGER.error('x-rate-limit-reset = %s', response.headers["x-rate-limit-reset"])
            break
        payload = response.json()
        res = payload.get('data', [])
        out.extend(res)
        LOGGER.info("Got %s results on page", len(res))
        if 'meta' not in payload or 'next_token' not in payload['meta']:
            break
        token = payload['meta']['next_token']
        LOGGER.info("Sleeping for %s seconds ...", sleep_time)
        time.sleep(sleep_time)
    return out


def get_following(user_id: str, app_id: int=0):
    url = (f'https://api.twitter.com/2/users/{user_id}/following?'
           f'max_results=1000&user.fields={USER_FIELDS}')
    #print(url)
    return __paginator(url, app_id)


def get_followers(user_id: str, app_id: int=0):
    url = (f'https://api.twitter.com/2/users/{user_id}/followers?'
           f'max_results=1000&user.fields={USER_FIELDS}')
    return __paginator(url, app_id)

def get_retweets(user_id: str, app_id: int=0):
    url = (f'https://api.twitter.com/1.1/statuses/retweets/{user_id}.json')
    return requests.get(url, headers=create_headers(app_id))

def __get_following_count(user: dict) -> int:
    try:
        return user['public_metrics']['following_count']
    except ValueError:
        return 0

def __get_allmylinks(driver: webdriver, url: str) -> str:
    if ALLMYLINKS_CARD.search(url):
        _r = requests.get(html.unescape(url))
        _s = (_r.headers['content-disposition'].split('"'))[1]
        _a = _s.replace('_business-card.jpeg', '')
        return f"https://allmylinks.com/{_a}"
    if ALLMYLINKS_QR.search(url):
        driver.get(url)
        try:
            _r = driver.find_element(By.CSS_SELECTOR, 'span.qr-code-view__name > em')
            return f"https://allmylinks.com/{_r.text[1:]}"
        except NoSuchElementException:
            LOGGER.error("Missing account name in %s", url)
    return url


def get_all_onlyfans(driver: webdriver, user: dict) -> list:
    """
    Get list of all unique onlyfans urls from twitter user dictionary
    """
    global twitter_acct
    twitter_acct = user["username"]
    if 'entities' not in user or 'url' not in user['entities']:
        return []
    _x = set()
    for _ent in user['entities'].values():
        if 'urls' not in _ent:
            continue
        for url in _ent['urls']:
            if 'expanded_url' in url:
                _u = url["expanded_url"]
            elif 'url' in url:
                _u = url["url"]
            else:
                LOGGER.info('Bad url:\n%s', json.dumps(url, indent=4))
                continue
            _tw = ONLYFANS_URL.search(_u)
            if _tw:
                LOGGER.info(_tw.string)
                _tw = [_tw.group(1).lower()]
            elif LINKTREE_URL.search(_u):
                _tw = get_linktree_onlyfans(driver, _u)
            elif GETSLINK_URL.search(_u):
                _tw = get_getslink_onlyfans(driver, _u)
            elif MYSLINK_URL.search(_u):
                _tw = get_getslink_onlyfans(driver, _u)
            elif LINKR_URL.search(_u):
                _tw = get_linkr_onlyfans(_u)
            else:
                _tw = []
                for _s, _p in LINK_SITES.items():
                    if not _p.search(_u):
                        continue
                    if 'allmylinks' in _u:
                        LOGGER.info("allmylinks: %s", _u)
                        _u = __get_allmylinks(driver, _u)
                    _twl = get_link_onlyfans(driver, _u)
                    if _twl:
                        _twl = list(set(_twl))
                        LOGGER.info('%s (%s)', _twl, _s)
                        _tw.extend(_twl)
            if _tw:
                _x.update(set(_tw))
    return list(_x)

def __close_other_windows(driver: webdriver):
    main_win = driver.window_handles[0]
    try:
        for _win in driver.window_handles[1:]:
            driver.switch_to.window(_win)
            driver.close()
    except (NoSuchWindowException, ProtocolError):
        pass
    driver.switch_to.window(main_win)

def __bypass_linktree_continue(driver: webdriver):
    try:
        #btn = driver.find_element(By.XPATH, '//button[contains(text(),"Continue")]')
        btn = WebDriverWait(driver, 2).until(
           EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"Continue")]')))
        btn.click()
        driver.execute_script("arguments[0].click();", btn)
        #LOGGER.info("Clicked continue")
        time.sleep(0.35)
        return True
    except (NoSuchElementException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException):
        #LOGGER.info("@@ No continue")
        pass

    try:
        btn = driver.find_element(By.XPATH, '//div[contains(text(),"over 18")]/../..')
        btn.click()
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.25)
        return True
    except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
        pass
    return False

def __bypass_linktree_dob(driver: webdriver) -> bool:
    dob = {'MM': '01', 'DD': '01', 'YYYY': '1970'}
    try:
        for _e, _t in dob.items():
            elem = WebDriverWait(driver, 2).until(
               EC.element_to_be_clickable((By.XPATH, f'//input[@placeholder="{_e}"]')))
            #elem = driver.find_element(By.XPATH, f'//input[@placeholder="{_e}"]')
            elem.send_keys(_t)
        btn = WebDriverWait(driver, 2).until(
           EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"Unlock")]')))
        btn.click()
        driver.execute_script("arguments[0].click();", btn)
        LOGGER.info("Entered DOB")
        time.sleep(0.25)
        return True
    except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
        #LOGGER.info("Nothing to do")
        return False


def get_linktree_onlyfans_core(driver: webdriver, url: str) -> [str]:
    """
    Get onlyfans url from linktree
    """
    LOGGER.info('linktr.ee --> %s', url)
    driver = scraper.get_url(driver, url)
    __bypass_linktree_continue(driver)

    retval = []
    elem_text = {}
    while True:
        try:
            for elem in driver.find_elements(By.XPATH, LINKTREE_ONLYFANS):
                #LOGGER.info("elem_text = %s", elem.text)
                elem_text[elem.text] = False
            for elem in driver.find_elements(By.XPATH, LINKTREE_ONLYFANS1):
                #LOGGER.info("elem_text = %s", elem.text)
                elem_text[elem.text] = False
            for elem in driver.find_elements(By.CSS_SELECTOR,  LINKTREE_ONLYFANS2):
                #LOGGER.info("elem_text = %s", elem.text)
                elem_text[elem.text] = False
            break
        except StaleElementReferenceException:
            LOGGER.error("StaleElementReferenceException getting onlyfans links - retry")
    if not elem_text:
        return None
    LOGGER.info(elem_text)
    #driver.save_screenshot('c:/temp/now-0.png')
    for elem_str in elem_text:
        #driver.save_screenshot(f'c:/temp/now-{elem_str}.png')
        LOGGER.info(f'-# looking for {elem_str}')
        try:
            btn = driver.find_element(By.XPATH, f'//*[normalize-space(text())="{elem_str}"]')
            driver.execute_script("arguments[0].click();", btn)
            #btn.click()
            #LOGGER.info(f'clicked [{elem_str}]')
            time.sleep(1)
        except (NoSuchElementException, ElementClickInterceptedException):
            LOGGER.error("can't click [%s]", elem_str)
            pass
        except StaleElementReferenceException:
            #LOGGER.info(f'Stale [{elem_str}]')
            time.sleep(0.15)
            pass
        __bypass_linktree_continue(driver)
        __bypass_linktree_dob(driver)
        time.sleep(0.8)

    try:
        for elem in driver.find_elements(By.CSS_SELECTOR,  'a[href*="onlyfans.com" i]'):
            #LOGGER.info(f'# [{elem.text}]')
            _m = ONLYFANS_URL.search(elem.get_attribute('href'))
            if _m:
                retval.append(_m.group(1))
                #LOGGER.info(f'# [{elem.text}] {_m.string} (linktr.ee)')
                LOGGER.info(f'\t{_m.string} (linktr.ee)')
    except NoSuchElementException:
        LOGGER.error("## can't get href for element")
    except TimeoutException:
        LOGGER.error("## TimeoutException")
    __close_other_windows(driver)
    return retval


def __dump_linktree_url(url: str):
    global linktree_available, twitter_acct
    url_stub = 'http://localhost:4444/?'
    _m = LINKTREE_URL.search(url)
    if not _m:
        return
    linktree_acct = _m.group(1).lower()
    #LOGGER.info('Adding %s to linktree URLs', url)
    LOGGER.info(json.dumps({'linktree': linktree_acct, 'twitter': twitter_acct}))
    with open(f'{scraper.get_home()}/linktree_accts', 'a+') as _fp:
        _fp.write(linktree_acct + '\n')
    if not linktree_available:
        return
    try:
        requests.get(url_stub + f'linktree={linktree_acct}&twitter={twitter_acct}')
        LOGGER.info("Sent to server")
    except (requests.exceptions.InvalidURL, requests.exceptions.ConnectionError):
        linktree_available = False


def get_linktree_onlyfans(driver: webdriver, url: str) -> [str]:
    retries = 0
    retval = []
    __dump_linktree_url(url)
    return []
    while retries < 3:
        try:
            retval = get_linktree_onlyfans_core(driver, url)
            break
        except Exception as e:
            driver = scraper.get_driver()
            LOGGER.error("Retrying [%s] after %s", url, e)
            retries += 1
    return retval


def __get_linktree_onlyfans(driver: webdriver, url: str) -> [str]:
    """
    Get onlyfans url from linktree
    """
    LOGGER.info(f'linktr.ee --> {url}')
    try:
        driver.get(url)
    except WebDriverException as exc:
        LOGGER.error("Error loading %s: %s", url, exc)
        return None
    __bypass_linktree_continue(driver)

    retval = []
    elem_text = {}
    while True:
        try:
            for elem in driver.find_elements(By.XPATH, LINKTREE_ONLYFANS):
                elem_text[elem.text] = False
            for elem in driver.find_elements(By.CSS_SELECTOR,  LINKTREE_ONLYFANS2):
                elem_text[elem.text] = False
            break
        except StaleElementReferenceException:
            LOGGER.error("StaleElementReferenceException getting onlyfans links - retry")
    if not elem_text:
        return None
    for elem_str in elem_text:
        try:
            btn = driver.find_element(By.XPATH, f'//*[normalize-space(text())="{elem_str}"]')
            driver.execute_script("arguments[0].click();", btn)
            LOGGER.info(f'clicked [{elem_str}]')
        except (NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException):
            LOGGER.info(f"can't click [{elem_str}]")
            pass
        try:
            btn = WebDriverWait(driver, 5).until(
               EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"Continue")]')))
            time.sleep(5)
            btn.click()
        except (NoSuchElementException, ElementClickInterceptedException):
            #LOGGER.info("## nosuch for continue")
            pass
        except TimeoutException:
            #LOGGER.info("## timeout waiting for continue")
            pass
    try:
        for elem in driver.find_elements(By.CSS_SELECTOR,  'a[href*="onlyfans.com" i]'):
            LOGGER.info('Checking [%s]', elem.text)
            _m = ONLYFANS_URL.search(elem.get_attribute('href'))
            if _m:
                retval.append(_m.group(1))
                LOGGER.info(f'\t{_m.string} (linktr.ee)')
    except NoSuchElementException:
        LOGGER.info("## can't get href for element")
    except TimeoutException:
        LOGGER.info("## TimeoutException")
    __close_other_windows(driver)
    return retval


def get_linkr_onlyfans(url: str) -> [str]:
    _r = requests.get(url).text
    LOGGER.info('\t%s (linkr.bio)', url)
    out = {}
    for _m in ONLYFANS_URL.findall(unquote(_r), re.I):
        out[_m.lower()] = 1
    return sorted(out.keys())

def get_getslink_onlyfans(driver: webdriver, url: str) -> [str]:
    """
    Get onlyfans url from getslink
    """
    driver.get(url)
    try:
        btn = WebDriverWait(driver, 4).until(
           EC.element_to_be_clickable((By.XPATH, '//div[@id="OnlyFans"]')))
        driver.execute_script("arguments[0].click();", btn)
        btn.click()
    except (NoSuchElementException, TimeoutException):
        #print("onlyfans link not found")
        return None
    time.sleep(0.2)
    if len(driver.window_handles) == 1:
        #print("No second window found")
        return None
    driver.switch_to.window(driver.window_handles[1])
    retval = None
    time.sleep(0.2)
    _m = ONLYFANS_URL.search(driver.current_url)
    if _m:
        retval = [_m.group(1)]
        #print(f'{retval} (getsl.ink)')
        LOGGER.info('\t%s (getsl.ink)', driver.current_url)
    __close_other_windows(driver)
    return retval


def get_link_onlyfans(driver: webdriver, url: str) -> [str]:
    """
    Parameters
    ----------
    driver : webdriver
    url : str

    Returns
    -------
    [str] list of onlyfans urls found
    """
    retval = []
    try:
        #driver.get(url)
        driver = scraper.get_url(driver, url)
        for link in driver.find_elements(By.CSS_SELECTOR,  "a[href*='nlyfans.com' i]"):
            _m = ONLYFANS_URL.search(unquote(link.get_attribute('href')))
            if _m:
                retval.append(_m.group(1))
    except NoSuchElementException:
        pass
    except WebDriverException:
        LOGGER.info("Cannot load %s", url)
    return retval

def main(app_id=0):
    home = scraper.get_home()
    args = __parse_args()
    user = get_user(args.user_id, app_id=app_id)
    if not user:
        LOGGER.info("Bad twitter handle/ID [%s]", args.user_id)
        return
    LOGGER.info("User id = %s", user['id'])

    initial = {}
    if args.initial_file:
        initial = load_file(args.initial_file)
        LOGGER.info('Got %s entries from %s', len(initial), args.initial_file)
    flwrs = [user]
    flwrs.extend(get_following(user['id'], app_id))

    driver = scraper.get_driver('firefox')
    latest = []
    for _u in flwrs:
        LOGGER.info('dict(user_id="%s", username="%s", following_count=%s),',
                    _u["id"], _u["username"], __get_following_count(_u))
        _q = get_all_onlyfans(driver, _u)
        if _q:
            latest.extend(_q)
    latest = sorted(set([_u.lower() for _u in latest if _u]) - set(initial.keys()))
    with open(f'{home}/pool/{user["username"]}', "w") as _fp:
        _fp.write(" ".join(latest))
    _latest = {_u: scraper.info(driver, _u) for _u in latest}
    if args.auto_add and initial:
        _filename = f'{home}/finals/onlyfans.{datetime.now().strftime("%Y%m%dT%H%M%S")}.json'
        _latest.update(initial)
    else:
        _filename = f'{home}/finals/{user["username"]}-{datetime.now().strftime("%Y%m%dT%H%M%S")}-final.json'
    out = OrderedDict({_k: _latest[_k] for _k in sorted(_latest) if _latest[_k]})
    with open(_filename, "w") as _fp:
        json.dump(out, _fp, indent=4)
    LOGGER.info('Successfully wrote %s to %s', len(out), _filename)


def load_file(path: str):
    with open(path) as fp:
        return json.load(fp)


def __parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user-id", dest="user_id", help="User ID or username")
    parser.add_argument("-i", "--initial", dest="initial_file", default='',
                        help="Name of file containing current known entries")
    parser.add_argument("-a", "--add", dest="auto_add", action="store_true",
                        default=False, help="User ID or username")
    parser.add_argument('--values', type=str, nargs='+')
    return parser.parse_args()


def _user(driver, user_id, initial={}, version=0):
    home = scraper.get_home()
    user = get_user(user_id, version)
    if not user:
        LOGGER.info("Bad twitter handle/ID [%s]", user_id)
        return
    LOGGER.info("User id = %s", user['id'])
    flwrs = [user]
    flwrs.extend(get_following(user['id'], version))
    onlies = []
    pq = {}
    for _u in flwrs:
        LOGGER.info('dict(version=%s, user_id="%s", username="%s", following_count=%s),',
                    version, _u["id"], _u["username"], __get_following_count(_u))
        _q = get_all_onlyfans(driver, _u)
        if _q:
            onlies.extend(_q)
            pq.update({_x.lower(): _u["username"].lower() for _x in _q})
    with open(f'{home}/pool/{user["username"]}', "w") as _fp:
        _fp.write(" ".join(onlies))
    latest = sorted(set([_u.lower() for _u in onlies if _u]) - set(initial.keys()))
    _latest = {_u: scraper.info(driver, _u) for _u in latest}
    for _u in latest:
        if _latest[_u]:
            _latest[_u]['twitter'] = pq[_u]
    _filename = f'{scraper.get_home()}/finals/{user["username"]}-{datetime.now().strftime("%Y%m%dT%H%M%S")}-final.json'
    out = OrderedDict({_k: _latest[_k] for _k in sorted(_latest) if _latest[_k]})
    with open(_filename, "w") as _fp:
        json.dump(out, _fp, indent=4)
    LOGGER.info('Successfully wrote %s to %s', len(out), _filename)
    return out
