import time
import argparse
from pathlib import Path
import re
import logging
import json
import twitter
import scraper

LOGGER = None

def set_logger(app_id: str):
    logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s.%(funcName)s %(message)s',
                        datefmt='%Y%m%d %H:%M:%S',
                        filename=f'{scraper.get_home()}/logs/batch_{app_id}.log',
                        level=logging.INFO)
    LOGGER = logging.getLogger(__name__)
    scraper.add_stderr_logging()

LAST_FILE = f'{scraper.get_home()}/last_processed_'

def write_last(twitter_account: str, filename: str):
    print(f"Writing {twitter_account} to {filename}")
    with open(filename, 'a') as _fp:
        _fp.write('\n' + twitter_account.lower())


def read_last(filename: str):
    with open(filename) as _fp:
        fin2 = sorted([_x for _x in _fp.read().lower().split('\n') if _x])
        #print(fin2[-10:])
        return fin2[-1].lower()
        #return _fp.read().strip()

def users_from_file(filename: str, version: str):
    with open(filename) as _fp:
        user_list = re.split(r'\s+', _fp.read())
    try:
        last = read_last(f'{LAST_FILE}{version}')
        logging.info("last = %s", last)
        _z = user_list.index(last) + 1
        #print(last, _z)

        logging.info("Starting after [%s] (version %s)", last, version)
        #print(f"Starting after [{last}]")
        return user_list[_z:]
    except:
        pass
    return user_list

def subset(dirname: str, version: str, pattern: str = "*final.json"):
    with open(f'{scraper.get_home()}/fiin.{version}') as _fp:
        user_list = sorted(set([_x for _x in re.split(r'\s+', _fp.read()) if _x]))
    logging.info("Got %s twitter handles", len(user_list))
    #print(f"Got {len(user_list)} twitter handles")

    try:
        last = read_last(f'{LAST_FILE}{version}')
        logging.info("last = %s", last)
        _z = user_list.index(last) + 1
        #print(last, _z)

        logging.info("Starting after [%s] (version %s)", last, version)
        #print(f"Starting after [{last}]")
        return user_list[_z:]
    except:
        pass
        #print(f"Couldn't find {last}")

    try:
        path = Path(dirname)
        files = path.glob(pattern)
        latest = max(files, key=lambda x: x.stat().st_ctime)
        _z = user_list.index((latest.name.split('-'))[0].lower()) + 1
        logging.info("Starting after [%s] (version %s)", user_list[_z], version)
        return user_list[_z:]
    except ValueError:
        return user_list


def __parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", type=int, required=True)
    parser.add_argument("-f", "--file", type=str)
    parser.add_argument("-b", "--browser", type=str, 
                        choices=['firefox', 'chrome'], default=None)
    return parser.parse_args()

def main():
    args = __parse_args()
    set_logger(args.version)
    if args.file:
        subst = users_from_file(args.file, args.version)
    else:
        subst = subset(f'{scraper.get_home()}/finals', args.version)
    with open(f'{scraper.get_home()}/of0.json') as fp:
        vv = json.load(fp)
    browser = args.browser if args.browser else 'firefox'
    driver = scraper.get_driver(browser)
    qq = {}
    for _u in subst:
        print(_u)
        _q = twitter._user(driver, _u, vv, args.version)
        if _q: qq[_u] = _q
        write_last(_u, f'{LAST_FILE}{args.version}')
        logging.info("Sleep between calls")
        time.sleep(67)


if __name__ == "__main__":
    main()
