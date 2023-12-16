 # -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 18:59:58 2022

@author: dwgre
"""
import re
import time
import logging
import scraper
import twitter

logging.basicConfig(
    handlers=[logging.FileHandler(filename=f'{scraper.get_home()}/logs/linktree.log',
                                  encoding='utf-8', mode='a+')],
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s.%(funcName)s %(message)s',
    datefmt='%Y%m%d %H:%M:%S',
    level=logging.INFO)
LOGGER = logging.getLogger(__name__)
#scraper.add_stderr_logging()
LINKTREE_URL = re.compile(r'^https?:\/\/linktr\.ee\/[A-Za-z0-9_.\-]+', re.I)

zfile = f'{scraper.get_home()}/linktree_onlyfans'
zdone = f'{scraper.get_home()}/linktree_accts.done'
def __read(filename):
    with open(filename) as _fp:
        return sorted({_x.lower() for _x in _fp.read().split("\n") if _x})

def __write(usernames, filename):
    with open(filename, 'a') as _fp:
        _fp.write("\n".join(sorted(set(usernames))))
        logging.info(f'Writing to {filename}')


def main() -> None:
    #with open(f'{twitter.scraper.get_home()}/linktree_urls') as _fp:
    urls = __read(f'{scraper.get_home()}/linktree_accts')
    logging.info(f'urls = {len(urls)}')
    
    with open(zdone) as _fp:
        done = _fp.read().split('\n')
    urls = sorted(set(urls) - set(done))
    logging.info(f'urls = {len(urls)}, done = {len(done)}')
    #sys.exit()
    
    usernames = __read(zfile)
    driver = twitter.scraper.get_driver('firefox')
    for i, acct in enumerate(urls):
        url = f'https://linktr.ee/{acct}'
        time.sleep(0.15)
        _x = twitter.get_linktree_onlyfans_core(driver, url)
        if isinstance(_x, list):
            usernames.extend(_x)
            if _x: logging.info('Got %s', _x)
        done.append(acct)
        if i > 0 and i % 10 == 0:
            __write(usernames, zfile)
            __write(done, zdone)
    __write(usernames, zfile)
    __write(done, zdone)
    driver.close()
    driver.quit()


if __name__ == "__main__":
    main()
