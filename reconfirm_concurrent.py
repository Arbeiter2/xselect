import sys
from datetime import datetime
import logging
import json
from concurrent.futures import ProcessPoolExecutor, as_completed, wait
import scraper

logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s.%(funcName)s %(message)s',
                    datefmt='%Y%m%d %H:%M:%S',
                    filename=f'{scraper.get_home()}/logs/reconfirm_concurrent.log',
                    level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def __write(out, id):
    _filename = f'{scraper.get_home()}/reconfirm/reconfirm-{id}-{datetime.now().strftime("%Y%m%dT%H%M%S")}.json'
    with open(_filename, 'w') as _fp:
        json.dump(out, _fp, indent=4)
    LOGGER.info('Successfully wrote %s to %s', len(out), _filename)


def run_process(id: int, accounts: list):
    LOGGER.info(f'Instance {id}: Processing from [{accounts[0]}] to [{accounts[-1]}]')
    driver = scraper.get_driver('chrome')
    qq = {}
    for _i, _u in enumerate(accounts):
        qq[_u] = scraper.info(driver, _u)
        if _i and _i % 500 == 0:
            __write(qq, id)
            qq = {}
    if qq:
        __write(qq, id)
    return True

def main():
    with open(f'{scraper.get_home()}/of0.json') as fp:
        vv = sorted(json.load(fp).keys())

    start = 10000
    futures = []
    # scrape and crawl
    with ProcessPoolExecutor() as executor:
        for number in range(5, 9):
            futures.append(
                executor.submit(run_process, number, vv[number * start:(number + 1) * start])
            )
    #wait(futures)
    for future in as_completed(futures):
        result = future.result()

if __name__ == "__main__":
    main()