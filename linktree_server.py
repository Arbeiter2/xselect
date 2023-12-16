# -*- coding: utf-8 -*-
"""
Created on Sun Aug  7 11:38:24 2022

@author: dwgre
"""
import time
from datetime import datetime
import json
from aiohttp import web
import asyncio
import logging
import scraper
import twitter

logging.basicConfig(
    handlers=[logging.FileHandler(filename=f'{scraper.get_home()}/logs/linktree_server.log',
                                  encoding='utf-8', mode='a+')],
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s.%(funcName)s %(message)s',
    datefmt='%Y%m%d %H:%M:%S',
    level=logging.INFO)
LOGGER = logging.getLogger(__name__)
LINKTREE_Q = None
DRIVER = twitter.scraper.get_driver('firefox')
SCRUMP = {}
MAX_SCRUMP = 10

ZFILE = f'{scraper.get_home()}/linktree_last'

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


async def consumer(queue):
    LOGGER.info("Consumer running")
    while True:
        entry = await queue.get()
        url = f'https://linktr.ee/{entry["linktree"]}'
        LOGGER.info('Processing %s', entry)
        await asyncio.sleep(5)
        try:
            onlies = twitter.get_linktree_onlyfans_core(DRIVER, url)
            LOGGER.info('Got %s', onlies)
        except Exception as _e:
            LOGGER.error(_e, exc_info=True)

        if isinstance(onlies, list):
            for _o in onlies:
                user = scraper.info(DRIVER, _o)
                if user:
                    user['twitter'] = entry['twitter']
                    SCRUMP[_o] = user
        __write()
        __last(entry)
        queue.task_done()
    return

def _bad_data():
    return web.json_response({'error': 'Missing mandatory fields'}, status=400)

def _accepted_data(acct: str):
    return web.json_response({'account': acct, 'status': 'OK'}, status=200)


async def get(request):
    _tw = request.rel_url.query.get('twitter', '')
    _lkt = request.rel_url.query.get('linktree', '')
    if not _tw or not _lkt:
        return _bad_data()
    await request.app['queue'].put({'twitter': _tw, 'linktree':_lkt})
    return _accepted_data(_lkt)


async def server(queue: asyncio.Queue):
    app = web.Application()
    app.add_routes([web.get('/', get)])
    app['queue'] = queue
    #web.run_app(app, host='0.0.0.0', port=4444)
    LOGGER.info("App created")

    try:
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 4444)
        await site.start()
        LOGGER.info("Web server running")
        await asyncio.sleep(100*3600)
    except Exception as _e:
        #LOGGER.info("Failed to start server %s", type(_e))
        LOGGER.error(_e, exc_info=True)
    await runner.cleanup()


async def main():
    queue = asyncio.Queue()
    print(queue)
 
    #await asyncio.gather(asyncio.create_task(server(queue)))
    _c = asyncio.create_task(consumer(queue))
    print("await consumer(queue)")

    await queue.join()
    print("await queue.join()")

    _s = asyncio.create_task(server(queue))
    print("await server(queue)")
    await asyncio.gather(_c, _s)
    return queue


if __name__ == '__main__':
#    queue = asyncio.run(main())
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    loop.close()
