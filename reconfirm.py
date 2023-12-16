import os
import sys
from datetime import datetime
import logging
import json
import scraper

logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s.%(funcName)s %(message)s',
                    datefmt='%Y%m%d %H:%M:%S',
                    filename=f'{scraper.get_home()}/logs/reconfirm{"_" + sys.argv[1] if len(sys.argv) > 1 else ""}.log',
                    level=logging.INFO)
LOGGER = logging.getLogger(__name__)
OUTPUT = f'{scraper.get_home()}/reconfirm'
ALL_DONE = []


def load():
    _fg = {}
    for _f in os.listdir(OUTPUT):
        with open(f'{OUTPUT}/{_f}') as fp:
            _fg.update(json.load(fp))
    return set(_fg.keys())


def last(all_entries: list):
    try:
        if len(sys.argv) > 1:
            return all_entries[int(sys.argv[1])+1:]
    except:
        return all_entries

def __write(out):
    if not out:
        return
    _filename = f'{OUTPUT}/reconfirm-{datetime.now().strftime("%Y%m%dT%H%M%S")}.json'
    with open(_filename, 'w') as _fp:
        json.dump(out, _fp, indent=4)
    LOGGER.info('Successfully wrote %s to %s', len(out), _filename)
    ALL_DONE = load()

def main():
    with open(f'{scraper.get_home()}/of0.json') as fp:
        vv = list(json.load(fp).keys())
    driver = scraper.get_driver('firefox')
    qq = {}
    subst = last(vv)
    logging.info(subst[0])
    ALL_DONE = load()
    epl = sorted(set(subst) - ALL_DONE)
    if not epl:
        LOGGER.info("Nothing to do")
        return
    LOGGER.info("Starting at: true: %s, actual: %s", subst[0], epl[0])
    for _i, _u in enumerate(epl):
        if _u in ALL_DONE:
            continue
        qq[_u] = scraper.info(driver, _u)
        if _i and _i % 100 == 0:
            __write(qq)
            qq = {}
    __write(qq)


if __name__ == "__main__":
    main()