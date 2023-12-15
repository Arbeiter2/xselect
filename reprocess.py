from datetime import datetime
import logging
import re
import json
import scraper

logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s.%(funcName)s %(message)s',
                    datefmt='%Y%m%d %H:%M:%S',
                    filename=f'{scraper.get_home()}/logs/reprocess.log',
                    level=logging.INFO)
LOGGER = logging.getLogger(__name__)
#LOGGER.addHandler(logging.StreamHandler())

DIGITS = re.compile(r'^\d+$')


zdone = f'{scraper.get_home()}/linktree_accts_processed.done'
def __read(filename):
    with open(filename) as _fp:
        return sorted({_x.lower() for _x in _fp.read().split("\n") if _x})

def __write(usernames, filename):
    with open(filename, 'a') as _fp:
        _fp.write("\n".join(usernames))
        #logging.info(f'Writing to {filename}')

with open(f'{scraper.get_home()}/linktree_onlyfans') as _fp:
#with open(f'{scraper.get_home()}/fin22') as _fp:
    vx = [_n.lower() for _n in _fp.read().split('\n') if _n]
with open(f'{scraper.get_home()}/of0.json') as fp:
    vv = json.load(fp)
try:
    with open(f'{scraper.get_home()}/finals/allfound.json') as fp:
        af = json.load(fp)
except FileNotFoundError:
    af = {}
last = __read(zdone)

newx = sorted([_x for _x in (set(vx) - set(vv) - set(af) - set(last)) if _x and not DIGITS.match(_x)])
LOGGER.info('Got %s entries', len(newx))

#last = __read(zdone)

#newx = newx[:newx.index(last[-1])] if last else newx
out = {}
driver = scraper.get_driver('firefox')
for _i, _u in enumerate(newx):
    out[_u] = scraper.info(driver, _u)
    if _i and _i % 100 == 0:
        __write(list(out.keys()), zdone)
        _filename = f'{scraper.get_home()}/finals/reprocess-{datetime.now().strftime("%Y%m%dT%H%M%S")}.json'
        with open(_filename, 'w') as _fp:
            json.dump(out, _fp, indent=4)
        LOGGER.info('Successfully wrote %s to %s', len(out), _filename)
        out = {}
__write(_u, zdone)
with open(_filename, 'w') as _fp:
    json.dump(out, _fp, indent=4)
LOGGER.info('Successfully wrote %s to %s', len(out), _filename)
