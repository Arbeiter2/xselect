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
LOGGER.addHandler(logging.StreamHandler())

DIGITS = re.compile(r'^\d+$')


zdone = f'{scraper.get_home()}/linktree_accts_processed.done'
def __read(filename):
    with open(filename) as _fp:
        return sorted({_x.lower() for _x in _fp.read().split("\n") if _x})

def __write(out):
    with open(zdone, 'a') as _fp:
        _fp.write("\n".join(sorted(out.keys())) + "\n")
    _filename = f'{scraper.get_home()}/finals/reprocess-{datetime.now().strftime("%Y%m%dT%H%M%S")}.json'
    with open(_filename, 'w') as _fp:
        json.dump(out, _fp, indent=4)
    LOGGER.info('Successfully wrote %s to %s', len(out), _filename)

with open(f'{scraper.get_home()}/linktree_onlyfans') as _fp:
#with open(f'{scraper.get_home()}/fin22') as _fp:
    vx = [_n.lower() for _n in _fp.read().split('\n') if _n]
with open(f'{scraper.get_home()}/of0.json') as fp:
    vv = json.load(fp)
last = __read(zdone)

newx = sorted([_x for _x in (set(vx) - set(vv) - set(last)) if _x and not DIGITS.match(_x)])
LOGGER.info('Got %s entries', len(newx))

out = {}
driver = scraper.get_driver('chrome')
for _i, _u in enumerate(newx):
    out[_u] = scraper.info(driver, _u)
    if _i and _i % 100 == 0:
        __write(out)
        out = {}
__write(out)
