import json
import scraper

driver = scraper.get_driver()
with open('/home/delano/bad_users') as fp:
    bad = [_x for _x in fp.read().split("\n") if _x]

with open('/home/delano/of0.json') as fp:
    users = json.load(fp)

real_bad = list(set(bad) - set(users.keys()))
for _u in sorted(real_bad):
    _z = scraper.info(driver, _u, True)
    if _z:
        _real_bad[_u] = _z

with open('/home/delano/reclaimed.json', 'w') as fp:
    json.dump(real_bad, fp, indent=4)
