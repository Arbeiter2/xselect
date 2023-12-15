# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 21: 42: 47 2021

@author: dwgreenidge
"""
import logging
import os
import platform
import sys
import re
import time
import requests
from pathlib import Path
from colorama import Fore
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import NoSuchElementException, TimeoutException,\
    StaleElementReferenceException, WebDriverException, InvalidSessionIdException 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium_profiles.profiles import profiles
from selenium.webdriver.remote.remote_connection import LOGGER as seleniumLogger
from urllib3.connectionpool import log as urllibLogger
from urllib3.exceptions import HTTPError, MaxRetryError, NewConnectionError

def is_docker():
    cgroup = Path("/proc/self/cgroup")
    return Path('/.dockerenv').is_file() or cgroup.is_file() and cgroup.read_text().find("docker") > -1

def get_home():
    if platform.machine() in ('armv7l', 'armv6l') or is_docker():
       return '/mnt/chronos'
    if sys.platform != 'win32':
        #return '/home/delano'
        return '/mnt/c/Users/dwgre/Documents/home'
    return 'H:'

LOGGER = logging.getLogger(__name__)

seleniumLogger.setLevel(logging.WARNING)
urllibLogger.setLevel(logging.WARNING)

ONLYFANS_USER_RE = re.compile(r'onlyfans.com\/([a-zA-Z][a-zA-Z0-9_\-.]+)')
ONLYFANS_URL_XPATH = '//a[contains(@href, "onlyfans.com/")]'
HEADERS = {'User-agent': 'yourbot'}
ONLYFANS_COUNTRY = '//*[contains(@href, "icon-location")]/../following-sibling::span/p'
WARNING = re.compile(r'warning\W*$', re.I)
SENTENCE = re.compile(r'(?!\S)\.\s+')
DISCLAIMER = re.compile(r'(legal (action|note)|creative work|disclaimer|you do not have|rights .*(belong|owned)|rights reserved|by law| permi|forbidden|protected|copyright|lawful|property|DCMA|DMCA|lawsuit|prosecute|legal|jurisdiction|distribut|enforcement|screenshot|acknowledge and agree|proprietary|prohibit|trademark| own .*content|content .+ own|any material|purchased through|unauth|reproduc|copy|terms and conditions)', re.I)

def add_stderr_logging():
    #for handler in LOGGER.handlers:
    #    if 'stderr' in str(handler):
    #        LOGGER.removeHandler(handler)
    LOGGER.addHandler(logging.StreamHandler())


def is_valid_onlyfans(driver: webdriver, account: str) -> bool:
    if account.lower() == 'action':
        return False
    url = f'https://www.onlyfans.com/{account}/media'
    try:
        #driver.get(url)
        driver = get_url(driver, url)
        driver.find_element(By.CSS_SELECTOR, '.b-404__title')
        return False
    except NoSuchElementException:
        return True
    except (WebDriverException, TimeoutException):
        return False

def strip_disclaimer(text):
    """
    Remove disclaimer text
    """
    out = []
    for paragraph in re.split('\n', text):
        #print(f'<p>: [{paragraph}]')
        sentences = SENTENCE.split(paragraph)
        #print(f'<s>: {sentences}')
        good = '. '.join([WARNING.sub('', _s)
                          for _s in sentences if not DISCLAIMER.search(_s)])
        out.append(good)
    return '\n'.join(out)


COMPONENTS = {'images': "image", 'video': "video", 'likes': "like", 'followers': "follow"}

def intify(stringval: str):
    if not stringval:
        return 0
    last_char = stringval[-1]
    if re.match('\d', last_char):
        factor = 1
    else:
        stringval = stringval[:-1]
        if last_char in ('K', 'k'):
            factor = 1e3
        elif last_char in ('M', 'm'):
            factor = 1e6
    try:
        f = float(stringval)
    except ValueError:
        return 0
    return int(f * factor)

def __header_info(driver: webdriver, component: str) -> str:
    try:
        _e = driver.find_element(By.XPATH, f'//*[contains(@href,"icon-{component}")]/../following-sibling::span')
        return intify(_e.text) if _e else 0
    except NoSuchElementException:
        return 0
    
def __pic_count(driver: webdriver) -> int:
    return __header_info(driver, COMPONENTS['images'])

def __video_count(driver: webdriver) -> int:
    return __header_info(driver, COMPONENTS['video'])

def __like_count(driver: webdriver) -> int:
    return __header_info(driver, COMPONENTS['likes'])

def __followers_count(driver: webdriver) -> int:
    return __header_info(driver, COMPONENTS['followers'])

def __country(driver: webdriver) -> str:
    try:
        _e = driver.find_element(By.XPATH, ONLYFANS_COUNTRY)
        #LOGGER.info(f'\t__country: {_e.text}')
        return _e.get_attribute("innerText")
    except NoSuchElementException:
        return ""

def __description(driver: webdriver) -> str:
    try:
        _img = driver.find_element(By.CSS_SELECTOR, ".b-user-info__text")
        #LOGGER.info(f'\t__description: {_img.text}')
        return strip_disclaimer(_img.text)
    except NoSuchElementException:
        return ""

def __user_name(driver: webdriver) -> str:
    try:
        _img = driver.find_element(By.CSS_SELECTOR, "div.g-user-name")
        #LOGGER.info(f'\t__user_name: {_img.text}')
        return _img.text
    except (StaleElementReferenceException, NoSuchElementException):
        return ""

def __main_image(driver: webdriver) -> str:
    try:
        _img = driver.find_element(By.CSS_SELECTOR, "img.b-profile__header__cover-img")
        #LOGGER.info(f"\t__main_image: {_img.get_attribute('src')}")
        return _img.get_attribute('src')
    except NoSuchElementException:
        return ''

def __avatar_image(driver: webdriver) -> str:
    try:
        div = driver.find_element(By.CSS_SELECTOR, ".g-avatar__img-wrapper")
        div.click()
        _img = driver.find_element(By.CSS_SELECTOR, "img.pswp__img")
        #LOGGER.info(f"\t__avatar_image: {_img.get_attribute('src')}")
        return _img.get_attribute('src')
    except NoSuchElementException:
        return ''

def __subscription_text(driver: webdriver) -> str:
    try:
        _s = driver.find_element(By.CSS_SELECTOR, 'div.b-offer-join')
        #LOGGER.info(f'\t__subscription_text: {_s.text}')
        return _s.text.replace('SUBSCRIBE\n', '')
    except NoSuchElementException:
        return ''


def __offers_text(driver: webdriver) -> list:
    try:
        offers = driver.find_elements(By.CSS_SELECTOR,  'div.m-promotion > div.g-btn')
        #LOGGER.info(f'\t__offers_text: {offers}')
        return [_o.text.replace('\n', ' ') for _o in offers]
    except (NoSuchElementException, StaleElementReferenceException):
        return []

TAG = re.compile(r'(.+) (\d+)\s*$')
def __tags(driver: webdriver) -> dict:
    try:
        tags = {}
        for _e in driver.find_elements(By.CSS_SELECTOR,  'span.b-tabs__nav__text'):
            _m = TAG.match(_e.text)
            if _m and _m.group(1) != 'All':
                tags[_m.group(1).lower()] = int(_m.group(2))
        return tags
    except (NoSuchElementException, StaleElementReferenceException):
        return {}

def get_media_summary(driver: webdriver, account: str):
    pics = __pic_count(driver)
    videos = __video_count(driver)
    if pics or videos:
        return {'photo': pics, 'video': videos}
    #url = f'https://www.onlyfans.com/{account}/media'
    #driver = get_url(driver, url)
    return __tags(driver)

def __get_twitter(driver: webdriver):
    try:
        e = driver.find_element(By.XPATH, "//*[@data-icon-name='icon-twitter-social']/parent::a")
    except NoSuchElementException:
        return None
    driver.get(e.get_attribute('href'))
    url = driver.current_url
    return (url.split("/"))[-1]

def info(driver: webdriver, account: str, fast=False) -> dict:
    timeout = 2 if fast else 10
    if not is_valid_onlyfans(driver, account):
        return {}
    try:
        WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.g-user-username"))).get_attribute("value")

        out = {
            'account': account,
            'description': __description(driver),
            'user_name': __user_name(driver),
            'country': __country(driver),
            'photo': __main_image(driver),
            'avatar': __avatar_image(driver),
            'cost': __subscription_text(driver),
            'offers': __offers_text(driver),
            'followers': __followers_count(driver),
            'likes': __like_count(driver),
            #'tags': __tags(driver),
            'media': get_media_summary(driver, account),
        }
        tw = __get_twitter(driver)
        if tw:
            out['twitter'] = tw.lower()
        LOGGER.info(Fore.RESET + '%s ' + Fore.GREEN + 'OK' + Fore.RESET, account)
        return out
    except (TimeoutException, NoSuchElementException) as exc:
        LOGGER.error(exc, exc_info=True)
    except (HTTPError) as exc:
        #LOGGER.critical(exc, exc_info=True)
        LOGGER.error("timeout on %s", account)
    LOGGER.info(Fore.RESET + '%s ' + Fore.RED + 'NOT OK' + Fore.RESET, account)
    return None

def get_images(driver: webdriver, account: str) -> dict:
    if not is_valid_onlyfans(driver, account):
        return {}
    try:
        WebDriverWait(driver, 2).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.g-user-username"))).get_attribute("value")

        out = {
            'photo': __main_image(driver),
            'avatar': __avatar_image(driver),
            'cost': __subscription_text(driver),
            'offers': __offers_text(driver),
            'followers': __followers_count(driver),
            'likes': __like_count(driver),
            'media': get_media_summary(driver, account),
        }
        return out
    except (TimeoutException, NoSuchElementException) as exc:
        #LOGGER.critical(exc, exc_info=True)
        print("timeout on %s [%s]" & (account, exc))
    return None



def __get_chrome_driver() -> webdriver:
    options = ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-setuid-sandbox") 
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument('--headless')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-extensions')
    options.add_argument("--disable-plugins-discovery")
    options.add_argument('--disable-dev-sh-usage')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-insecure-localhost')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument("--enable-automation")
    options.add_argument("--dns-prefetch-disable")
    options.add_argument("--disable-blink-features=AutomationControlled")
    #options.add_experimental_option("excludeSwitches", ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', True)
    options.add_experimental_option("prefs", {
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_setting_values.notifications": 2,
        "profile.managed_default_content_settings.stylesheets": 2,
        "profile.managed_default_content_settings.cookies": 2,
        "profile.managed_default_content_settings.javascript": 1,
        "profile.managed_default_content_settings.plugins": 1,
        "profile.managed_default_content_settings.popups": 2,
        "profile.managed_default_content_settings.geolocation": 2,
        "profile.managed_default_content_settings.media_stream": 2,
    })
    #options.set_capability("loggingPrefs", {'performance': 'ALL'})
    #options.set_capability("goog:loggingPrefs", {'performance': 'ALL'})    
    options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"')    
    if sys.platform != 'win32':
        exe_path = '/usr/bin/chromedriver'
    else:
        exe_path = rf"{os.environ['USERPROFILE']}\chromedriver\116\chromedriver.exe"
    driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=options
             )
    return driver

def __get_firefox_driver() -> webdriver:
    options = FirefoxOptions()
    options.headless = True
    agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    options.set_preference("general.useragent.override", agent)
    options.add_argument("start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    cap = DesiredCapabilities().FIREFOX
    cap['marionette'] = False
    if platform.machine().startswith('armv'):
        options.binary_location = r'/usr/bin/firefox-esr'
        driver = webdriver.Firefox(service=Service('/usr/bin/geckodriver'), options=options, desired_capabilities=cap)
    elif is_docker():
        options.binary_location = '/opt/firefox/firefox'
        driver = webdriver.Firefox(options=options, desired_capabilities=cap, service=Service('/usr/local/bin/chromedriver'))
    else:
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()),
                                   options=options)
    return driver
    

def __get_undetected() -> webdriver:
    import undetected_chromedriver as uc
    profile = profiles.Windows()
    options = uc.ChromeOptions()
    options.headless = True
    options.add_argument("--disable-extensions")
    options.add_argument('--disable-application-cache')
    options.add_argument('--disable-gpu')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    other_kwargs = {"version_main": 116, "profile": profile}
    if platform.machine() in ('armv7l', 'armv6l'):
        other_kwargs = {"driver_executable_path": "/usr/bin/chromedriver", "version_main": 106}
    return uc.Chrome(use_subprocess=True, service=ChromeService(), options=options, **other_kwargs) 


def get_driver(version='chrome') -> webdriver:
    #if platform.machine() in ('armv7l', 'armv6l'):
    #    driver = webdriver.Firefox()
    if version == 'chrome':
        driver = __get_chrome_driver()
    elif version == 'firefox':
        driver = __get_firefox_driver()
    elif version == 'und':
        driver = __get_undetected()
    driver.set_window_size(1920, 2160)
    driver.set_page_load_timeout(10)
    driver.implicitly_wait(2)
    return driver

def recycle(driver):
    name = driver.name
    try:
        driver.close()
        driver.quit()
    except:
        print("Driver closed")
        pass
    del driver
    time.sleep(3)
    LOGGER.info("Creating new webdriver")
    driver = get_driver(name)
    LOGGER.info("Webdriver created")
    return driver
    
def get_url(driver, url) -> webdriver:
    #print(url)
    _i = 0
    _good = False
    while _i < 3:
        try:
            driver.get(url)
            _good = True
            break
        except (MaxRetryError, NewConnectionError, ConnectionRefusedError, InvalidSessionIdException):
            LOGGER.error("MaxRetryError on %s", url)
            break
        except (HTTPError, WebDriverException, TimeoutException) as e: #:
            LOGGER.error("Exception in webdriver opening [%s]: %s", url, e)
            if 'ERR_NAME_NOT_RESOLVED' in str(e):
                raise e
            time.sleep(0.25)
            #driver.refresh()
            _i = _i + 1
    if _good:
        return driver
    # test the url
    try:
        requests.get(url)
    except:
        raise WebDriverException('Bad url')
    driver = recycle(driver)
    driver.get(url)
    return driver
