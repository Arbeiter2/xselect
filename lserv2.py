# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 18:13:18 2022

@author: dwgre
"""
import sys
from datetime import datetime
import json
import logging
import argparse
from aiohttp import web
import scraper
import twitter

if sys.platform == 'win32':
    from pipes.windows import WindowsPipe as Pipe
else:
    from pipes.linux import UnixPipe as Pipe

logging.basicConfig(
    handlers=[logging.FileHandler(filename=f'{scraper.get_home()}/logs/linktree_server.log',
                                  encoding='utf-8', mode='a+')],
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s.%(funcName)s %(message)s',
    datefmt='%Y%m%d %H:%M:%S',
    level=logging.INFO)
LOGGER = logging.getLogger(__name__)
DRIVER = None
SCRUMP = {}
MAX_SCRUMP = 10
ZFILE = f'{scraper.get_home()}/linktree_last'
done = {}

def init():
    global done
    with open(f'{scraper.get_home()}/linktree_accts.done') as _fp:
        done = {_x: 1 for _x in _fp.read().split('\n') if _x}
    LOGGER.info("Found {len(done)} entries already processed")
    return done

def __zwrite(username):
    with open(f'{scraper.get_home()}/linktree_accts.done', 'a') as _fp:
        _fp.write(f"\n{username}")

def __last(entry: dict):
    with open(ZFILE, 'w') as _fp:
        json.dump(entry, _fp)

def __write(force: bool = False):
    if not force and len(SCRUMP) < MAX_SCRUMP:
        return
    _filename = f'{scraper.get_home()}/finals/linktree_server-{datetime.now().strftime("%Y%m%dT%H%M%S")}-final.json'
    LOGGER.info(f'Writing to {_filename}')
    with open(_filename, 'w') as _fp:
        json.dump(SCRUMP, _fp)
    SCRUMP.clear()


def get_onlyfans(entry: dict):
    global done
    if entry['linktree'] in done:
        LOGGER.info('Ignoring ["%s"] - already processed', entry['linktree'])
        return
    LOGGER.info('Processing %s', entry)
    done[entry['linktree']] = 1
    __zwrite(entry['linktree'])
    try:
        url = f'https://linktr.ee/{entry["linktree"]}'
        onlies = twitter.get_linktree_onlyfans_core(DRIVER, url)
        LOGGER.info('Got %s', onlies)
    except Exception as _e:
        LOGGER.error(_e, exc_info=True)
        return

    if isinstance(onlies, list):
        for _o in onlies:
            user = scraper.info(DRIVER, _o)
            if user:
                user['twitter'] = entry['twitter']
                SCRUMP[_o] = user
    __write()
    __last(entry)
    
def consumer():
    init()
    pipe = Pipe(server=False)
    pipe.open_reader()
    LOGGER.info("Consumer running")
    while True:
        try:
            data = pipe.read(1024)
        except ValueError:
            __write(force=True)
            break
        LOGGER.info("Got data = %s", data.strip())
        json_data = json.loads(data)
        # do slow processing
        get_onlyfans(json_data)
    LOGGER.info("Consumer terminated")
 
def web_server():
    async def handler(request):
        _tw = request.rel_url.query.get('twitter', '')
        _lkt = request.rel_url.query.get('linktree', '')
        if not _tw or not _lkt:
            return web.json_response({'error': 'Missing mandatory fields'},
                                     status=400)
        payload = {'twitter': str(_tw), 'linktree': str(_lkt)}
        LOGGER.info("payload = %s", payload)
        pipe.write(json.dumps(payload).encode())
        return web.json_response({'account': _lkt, 'status': 'OK'}, status=200)
    pipe = Pipe()
    app = web.Application()
    app.add_routes([web.get('/', handler)])
    LOGGER.info("Webserver running")
    web.run_app(app, host='0.0.0.0', port=4444)


def __parse_args():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-c", "--consumer", default=False, action="store_true")
    group.add_argument("-s", "--server", default=False, action="store_true")
    return parser.parse_args()


def main():
    global DRIVER
    args = __parse_args()
    if args.server:
        web_server()
    if args.consumer:
        DRIVER = twitter.scraper.get_driver('firefox')
        consumer()


if __name__ == "__main__":
    main()
