import sys
import json
from datetime import datetime
import logging
import twitter, scraper

SCRUMP = {}
LATEST = []
MAX_SCRUMP = 10
ZFILE = f'{scraper.get_home()}/linktree_last'
DFILE = f'{scraper.get_home()}/linktree_accts.done'

def set_logging():
    logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s.%(funcName)s %(message)s',
                        datefmt='%Y%m%d %H:%M:%S',
                        filename=f'{scraper.get_home()}/logs/linktree_v2.log',
                        level=logging.INFO,
                        encoding='utf-8')
    _logging = logging.getLogger(__name__)
    scraper.add_stderr_logging()


def __zwrite(username):
    with open(DFILE, 'a') as _fp:
        _fp.write(f"\n{username}")

def __last(entry: dict):
    with open(ZFILE, 'w') as _fp:
        json.dump(entry, _fp)

def __write(force: bool = False):
    if not force and len(SCRUMP) < MAX_SCRUMP:
        return
    _filename = f'{scraper.get_home()}/finals/linktree_server-{datetime.now().strftime("%Y%m%dT%H%M%S")}-final.json'
    with open(_filename, 'w') as _fp:
        json.dump(SCRUMP, _fp, indent=4)
    logging.info('Wrote %s to %s', len(SCRUMP), _filename)
    _latest = '\n'.join(LATEST)
    __zwrite(_latest)
    LATEST.clear()
    SCRUMP.clear()

def process_raw(filename: str):
    logging.info('Opening %s', filename)
    print(f'Opening {filename}', flush=True)
    with open(filename) as fp:
        #bbn = json.loads('[\n' + ',\n'.join(fp.read().strip().split('\n')) + ']')
        bbn = json.load(fp)
    with open(DFILE) as fp:
        done = fp.read().split('\n')
    nxt = {_x['linktree']: _x for _x in bbn}
    _d = set(nxt) - set(done)
    ret_val = [_x for _x in bbn if _x['linktree'] in (_d)]
    logging.info('Processing %s entries', len(ret_val))
    print(f'Processing {len(ret_val)} entries', flush=True)

    return ret_val

def main():
    set_logging()
    with open(f'{scraper.get_home()}/of0.json') as fp:
        vv = json.load(fp)
    unp = process_raw(sys.argv[1])
    if len(unp) == 0:
        return
    driver = scraper.get_driver('firefox')
    for entry in unp:
        print(entry, flush=True)
        LATEST.append(entry['linktree'])
        logging.info(entry)
        try:
            url = f'https://linktr.ee/{entry["linktree"]}'
            onlies = twitter.get_linktree_onlyfans_core(driver, url)
        except Exception:
            continue
        if not isinstance(onlies, list) or not onlies:
            continue
        onlies = sorted(set(onlies) - set(vv))
        if not onlies:
            continue
        logging.info('Got %s', onlies)
        print(f'Got {onlies}', flush=True)
        for _o in onlies:
            user = scraper.info(driver, _o)
            if user:
                user['twitter'] = entry['twitter']
                SCRUMP[_o.lower()] = user
        __write()
        __last(entry)
    __write(True)
    print("Complete")
    logging.info("Complete")


if __name__ == "__main__":
    main()
