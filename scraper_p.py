#####
# scraper_pyp
#####

import re
import asyncio
from pyppeteer import launch
from pyppeteer.browser import Browser
from pyppeteer_stealth import stealth

import scraper

ONLYFANS_COUNTRY = '//*[contains(@href, "icon-location")]/../following-sibling::span/p'


async def is_valid_onlyfans(page: Browser, account: str) -> bool:
    if account.lower() == 'action':
        return False
    url = f'https://www.onlyfans.com/{account}'
    try:
        await page.goto(url)
        await page.waitForSelector('.b-404__title', timeout=5e3)
        return False
    except:
        return True

COMPONENTS = {'images': "image", 'video': "video", 'likes': "like", 'followers': "follow"}

def intify(stringval: str):
    last_char = stringval[-1]
    if re.match('\d', last_char):
        factor = 1
    else:
        stringval = stringval[:-1]
        if last_char in ('K', 'k'):
            factor = 1e3
        elif last_char in ('M', 'm'):
            factor = 1e6
    return int(float(stringval) * factor)


async def __header_info(page: Browser, component: str) -> str:
    _e = await page.Jx(f'//*[contains(@href,"icon-{component}")]/../following-sibling::span')
    if _e:
        return intify(await page.evaluate('(element) => element.textContent', _e[0]))
    return 0
    
async def __pic_count(page: Browser) -> int:
    return __header_info(page, COMPONENTS['images'])

async def __video_count(page: Browser) -> int:
    return __header_info(page, COMPONENTS['video'])

async def __like_count(page: Browser) -> int:
    return __header_info(page, COMPONENTS['likes'])

async def __followers_count(page: Browser) -> int:
    return __header_info(page, COMPONENTS['followers'])

async def __country(page: Browser) -> str:
    _e = await page.Jx(ONLYFANS_COUNTRY)
    if _e:
        return await page.evaluate('(element) => element.innerText', _e[0])
    return ""

async def __description(page: Browser) -> str:
    _e = await page.J(".b-user-info__text")
    if not _e:
        return ""
    return scraper.strip_disclaimer(await page.evaluate('(element) => element.innerText', _e))

async def __user_name(page: Browser) -> str:
    _e = await page.J("div.g-user-name")
    return await page.evaluate('(element) => element.innerText', _e)


async def __main_image(page: Browser) -> str:
    _e = await page.J("img.b-profile__header__cover-img")
    return await page.evaluate('(element) => element.getAttribute("class")', _e)

async def __avatar_image(page: Browser) -> str:
    _e = await page.J("div.b-profile__user > a.g-avatar > img")
    return await page.evaluate('(element) => element.getAttribute("class")', _e)

async def __subscription_text(page: Browser) -> str:
    _s = await page.J('div.b-offer-join')
    return await page.evaluate('(element) => element.innerText', _s).replace('SUBSCRIBE\n', '')


async def __offers_text(page: Browser) -> list:
    return await page.querySelectorAllEval('div.m-promotion > div.g-btn', '(element) => element.innerText')


async def get_media_summary(page: Browser, account: str):
    pics = await __pic_count(page)
    videos = await __video_count(page)
    if pics or videos:
        return {'photo': pics, 'video': videos}
    return {}

async def info(page: Browser, account: str, fast=False) -> dict:
    timeout = 2 if fast else 10
    if not await is_valid_onlyfans(page, account):
        return {}

    out = {
        'account': account,
        'description': await __description(page),
        'user_name': await __user_name(page),
        'country': await __country(page),
        'photo': await __main_image(page),
        'avatar': await __avatar_image(page),
        'cost': await __subscription_text(page),
        'offers': await __offers_text(page),
        'followers': await __followers_count(page),
        'likes': await __like_count(page),
        #'tags': __tags(page),
        'media': await get_media_summary(page, account),
    }
    return out


async def main():
    browser = await launch(headless=True)
    page = await browser.newPage()
    await stealth(page) 
    accounts = ['proudleaf', 'leafdproud']
    for _a in accounts:
        print(f'{_a}::')
        print(await info(page, _a))
    await browser.close()

asyncio.get_event_loop().run_until_complete(main())

