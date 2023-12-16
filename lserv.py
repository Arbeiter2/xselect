# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 18:13:18 2022

@author: dwgre
"""
from datetime import datetime
import json
import logging
from multiprocessing import Process, Queue, Event
from aiohttp import web
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
DRIVER = twitter.scraper.get_driver('chrome')
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

class WebConsumer:
    def __init__(self):
        self.queue = Queue()
        self.signal = Event()
        self.server = None
        self.processor = None
        LOGGER.info("WebConsumer created")

    def __last(self, entry: dict):
        with open(ZFILE, 'w') as _fp:
            json.dump(entry, _fp)
    
    def __write(self, force: bool = False):
        if not force and len(SCRUMP) < MAX_SCRUMP:
            return
        _filename = f'{scraper.get_home()}/finals/linktree_server-{datetime.now().strftime("%Y%m%dT%H%M%S")}-final.json'
        LOGGER.info(f'Writing to {_filename}')
        with open(_filename, 'w') as _fp:
            json.dump(SCRUMP, _fp)
        SCRUMP.clear()


    def hhh(self, entry: dict):
        url = f'https://linktr.ee/{entry["linktree"]}'
        LOGGER.info('Processing %s', entry)
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
        self.__write()
        self.__last(entry)
        
    def consumer(self):
        LOGGER.info("Consumer running")
        self.signal.wait()
        while True:
            self.signal.wait()
            self.signal.clear()
            data = self.queue.get()
            LOGGER.info(f"Got data = {data}")
            if not data:
                break
            # do slow processing
            self.hhh(data)
        LOGGER.info("Consumer terminated")
     
    def web_server(self):
        async def handler(request):
            _tw = request.rel_url.query.get('twitter', '')
            _lkt = request.rel_url.query.get('linktree', '')
            if not _tw or not _lkt:
                return web.json_response({'error': 'Missing mandatory fields'},
                                         status=400)
            self.queue.put_nowait({'twitter': _tw, 'linktree':_lkt})
            self.signal.set()
            return web.json_response({'account': _lkt, 'status': 'OK'}, status=200)

        app = web.Application()
        app.add_routes([web.get('/', handler)])
        LOGGER.info("Webserver running")
        web.run_app(app, host='0.0.0.0', port=4444)
    
    def start(self):
        self.server = Process(target=self.web_server, name="web_server")
        self.server.start()
        #LOGGER.info(self.server, self.server.is_alive())

        self.processor = Process(target=self.consumer, name="consumer")
        self.processor.start()
        #LOGGER.info(self.processor, self.processor.is_alive())
        
def main():
    srv = WebConsumer()
    srv.start()

if __name__ == "__main__":
    main()
