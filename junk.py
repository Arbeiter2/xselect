# -*- coding: utf-8 -*-
"""
Created on Mon Aug  8 09:58:29 2022

@author: dwgre
"""

import asyncio
from aiohttp import web


async def handler(request):
    return web.Response(text="OK")


async def main():
    server = web.Server(handler)
    runner = web.ServerRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 4444)
    await site.start()

    print("======= Serving on http://127.0.0.1:8080/ ======")

    # pause here for very long time by serving HTTP requests and
    # waiting for keyboard interruption
    #await asyncio.sleep(100*3600)


loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(main())
except KeyboardInterrupt:
    pass
loop.close()