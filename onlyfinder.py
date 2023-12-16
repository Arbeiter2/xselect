# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 22:30:38 2023

@author: dwgre
"""
from collections import OrderedDict
import sys
import re
import time
from datetime import datetime
import logging
import argparse
import json
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException,\
    StaleElementReferenceException, WebDriverException, InvalidSessionIdException 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import scraper

NON_DIGIT = re.compile(r'\D+')
NON_WORD = re.compile(r'\W+')
PROFILE_RESULT_PREFIX = '#resultsProfiles div.result'
IMG_RESULT_PREFIX = '#resultsImages div.result-image'
ONLYFINDER_TERMS = {}
OF0 = {}
MAX_PROFILES = range(264, 270)
URL = "onlyfindersearch.com"

def reset_log(group):
    with open(f'{scraper.get_home()}/_only/cache/{group}.log', 'w') as fp:
        fp.write("")


def write_log(group, term):
    with open(f'{scraper.get_home()}/_only/cache/{group}.log', 'a') as fp:
        fp.write(f"{term}\n")

def read_log(group):
    try:
        with open(f'{scraper.get_home()}/_only/cache/{group}.log') as fp:
            return [x for x in fp.read().split("\n") if x]
    except:
        pass
    return []


def scroll(driver, search_term, selector, timeout):
    scroll_pause_time = timeout
    page_nr = 1
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        res = driver.find_elements(By.CSS_SELECTOR, selector)
        LOGGER.info("[%s]: %s Found %s results", search_term, page_nr, len(res))
        page_nr += 1
    
        # Wait to load page
        time.sleep(scroll_pause_time)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # If heights are the same it will exit the function
            break
        last_height = new_height

def location_term(**kwargs) -> str:
    #novia location:"Madrid, Spain",50km
    #novia-location%3a"madrid%2c-spain"%2c50km
    return f"-location%3a\"{kwargs['city']}%2c-{kwargs['country']}\"%2c{kwargs['radius']}km"

def get_profile_entries(driver, term, printable) -> dict:
    out = {}
    count = 0
    url = f"https://{URL}/{term}/profiles/"
    print(f"url = {url}")
    driver.get(url)
    driver.save_screenshot(f"{scraper.get_home()}/sps.png")

    try:
        WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.container.result-stats")))
        scroll(driver, printable, PROFILE_RESULT_PREFIX, 5)
        a = ActionChains(driver)
        res, count = __get_next(driver, term, printable, a)
        out.update(res)
    except (TimeoutException, NoSuchElementException) as exc:
        LOGGER.error(exc, exc_info=True)
        pass
    return out, count


def get_images(driver, term, printable):
    # use /images as in
    # /location%3a"bogota%2c-colombia"%2c50km-male/images/
    # use scroll to get to the bottom of the page
    # find all elements matching ".div-result-image a"
    # get a.href and a.data-username
    # run scraper.info on username
    out = {}
    url = f"https://{URL}/{term}/images/"
    print(f"url = {url}")
    driver.get(url)
    try:
        WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.container.result-stats")))
        scroll(driver, printable, IMG_RESULT_PREFIX, 5)
    except (TimeoutException, NoSuchElementException) as exc:
        LOGGER.error(exc, exc_info=True)
        pass
    _res = driver.find_elements(By.CSS_SELECTOR, "div.result-image a")
    res = sorted(set(_x.get_attribute('data-username') for _x in _res))
    LOGGER.info(f"Found {len(res)} results for [{printable}]")
    for account in res:
        if account not in OF0:
            profile = scraper.info(driver, account)
            if profile:
                out[account] = profile
    LOGGER.info(f"Found {len(out)} confirmed results for [{printable}]")
    _filename = f'{scraper.get_home()}/finals/{printable.replace(", ", "-")}-{datetime.now().strftime("%Y%m%dT%H%M%S")}.json'
    _out = OrderedDict({_k: out[_k] for _k in sorted(out) if out[_k]})
    with open(_filename, "w") as _fp:
        json.dump(_out, _fp, indent=4)
    LOGGER.info('Successfully wrote %s to %s', len(_out), _filename)


def __get_next(driver, term, printable, action):
    payload = {}
    res = driver.find_elements(By.CSS_SELECTOR, PROFILE_RESULT_PREFIX)
    LOGGER.info(f"Found {len(res)} results for [{printable}]")
    for elem in res:
        out = {}
        _u = elem.find_element(By.CSS_SELECTOR, 'div.img-avatar')
        username = _u.get_attribute('data-username')
        if username in OF0:
            continue
        out['username'] = username
        out['description'] = elem.find_element(By.CSS_SELECTOR, 'div.about').text
        for _e in elem.find_elements(By.CSS_SELECTOR, 'div.profile-info > span'):
            title_number = _e.get_attribute('textContent').replace(",", "")
            if ':' in title_number:
                continue
            title, number = NON_WORD.split(title_number)
            number = int(NON_DIGIT.sub('', number))
            out[title.lower()] = number
        out['twitter'] = ''
        try:
            twt = elem.find_element(By.CSS_SELECTOR, 'a[data-type*="twitter"]')  
            action.move_to_element(twt).perform()
            out['twitter'] = twt.get_attribute('href').replace('https://twitter.com/', '')
        except:
            pass
        out['is_ad'] = len(elem.find_elements(By.CSS_SELECTOR, 'span.isad')) > 0
        payload[out['username']] = out
        LOGGER.info("term = %s, username = %s%s", printable, username, (" (ad)" if out['is_ad'] else ""))
    return payload, len(res)

def tidy_search_term(search_term):
    bits = search_term.split(", ")
    if len(bits) == 1:
        return search_term
    return "location%3a%22" + "%2c-".join(bits) + "%22%2c50km"

def search(driver, term, mega, location, location_str):
    mega_list = [None]
    if mega:
        mega_list = sorted(set(ONLYFINDER_TERMS["random"]) - set(read_log(term)))
        if len(mega_list) == len(set(ONLYFINDER_TERMS["random"])):
            mega_list = [None] + mega_list
       
    for sub_search in mega_list:
        printable_stub = printable = term
        subt = f"{tidy_search_term(term)}"
        print(f"subt = {subt}")
        subt_set = {}
        if sub_search:
            subt = f"{subt}-{sub_search}"
            printable_stub = printable_stub + f"-{sub_search}"
            print(f"now subt = {subt}, printable_stub = {printable_stub}")
        for gender in ("male", "female"):
            gt = f"{subt}-{gender}"
            printable = printable_stub + f"-{gender}"
            if location and 'location' not in subt:
                gt = f"{gt}{location}"
                printable = printable + f"-{location_str}"
            entries, _ = get_profile_entries(driver, gt, printable)
            LOGGER.info("[%s] = %s entries", printable, len(entries))
            for _v in entries.values():
                _v['gender'] = gender
            subt_set.update(entries)
            #if True: #count in MAX_PROFILES:
            #    get_images(driver, gt, printable)
        file = f'{scraper.get_home()}/onlyfinder/{printable_stub.replace(", ", "-")}-{datetime.now().strftime("%Y%m%dT%H%M%S")}.json'
        with open(file, 'w') as fp:
            json.dump(subt_set, fp, indent=4)
        LOGGER.info(f"Wrote {len(subt_set)} to {file}")
        if mega:
            write_log(term, sub_search)  


def get_parser():
    parser = argparse.ArgumentParser(description='Scrape onlyfinder.com')
    parser.add_argument('query', type=str, help="Query term")
    parser.add_argument('-m', '--mega', action='store_true', default=False,
                        help='Run mega search')
    parser.add_argument('-f', '--force', action='store_true', default=False,
                        help='Force restart on standard list')
    parser.add_argument('-c', '--city', type=str)
    parser.add_argument('-y', '--country', type=str)
    parser.add_argument('-k', '--radius-km', type=int)
    return parser


def bypass(driver):
    print("starting bypass ...")
    driver.execute_script('''window.open("http://{URL}","_blank");''') # open page in new tab
    time.sleep(10) # wait until page has loaded
    driver.switch_to.window(window_name=driver.window_handles[0])   # switch to first tab
    driver.close() # close first tab
    driver.switch_to.window(window_name=driver.window_handles[0] )  # switch back to new tab
    time.sleep(10)
    driver.get("https://google.com")
    time.sleep(2)
    print("Bypass complete?")

if __name__ == "__main__":
    with open(f'./onlyfinder.json') as fp:
        ONLYFINDER_TERMS = json.load(fp)
    args = get_parser().parse_args() 
    location = ""
    location_str = ""
    if args.city and args.country and args.radius_km:
        location = location_term(city=args.city.lower(), country=args.country.lower(), radius=args.radius_km)
        location_str = f"-{args.city}-{args.country}-{args.radius_km}km"
    logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s.%(funcName)s %(message)s',
                    datefmt='%Y%m%d %H:%M:%S',
                    filename=f'{scraper.get_home()}/logs/onlyfinder/{args.query.replace(", ", "-")}{location_str}.log',
                    level=logging.INFO)
    LOGGER = logging.getLogger(__name__)
    driver = scraper.get_driver('und')
    with open(f'{scraper.get_home()}/of0.json') as fp:
        OF0 = json.load(fp)
    terms = [args.query]

    if args.query in ONLYFINDER_TERMS and args.query != "random":
        if args.force:
            reset_log(args.query)
        terms = sorted(set(ONLYFINDER_TERMS[args.query]) - set(read_log(args.query)))
        print(f"len(terms) = {len(terms)}")
    for search_term in terms:
        LOGGER.info("search_term = %s", search_term)
        search(driver, search_term, args.mega, location, location_str)
        write_log(args.query, search_term)
