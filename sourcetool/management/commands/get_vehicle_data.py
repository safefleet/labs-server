import hashlib as h
import asyncio
import aiohttp

import async_timeout
import time

import json
import redis

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):

    def add_arguments(self, parser):
        # parser.add_argument('--show', action='store_true', dest='show')
        pass

    def handle(self, *args, **options):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._main())

    async def _main(self):

        redis_que = RedisQueue('vehicles', charset='utf-8', decode_responses=True)

        async with aiohttp.ClientSession() as session:
            while True:

                # get
                req_all_data = await self.fetch_all_vehicle_data(
                    session,
                    'https://alpha.safefleet.eu/safefleet/api/get_current_positions',
                    self._create_login_params())

                # mapped json
                new_vehicle_data = self.adapt_all_vehicle_data(req_all_data)

                # post
                await self.post_all_vehicle_data(
                    session,
                    'http://127.0.0.1:8000/sourcetool/',
                    new_vehicle_data)

                # save to redis que
                json_vehicle_data = json.dumps(new_vehicle_data)
                redis_que.put(json_vehicle_data)

                # testing code
                # unpacked = json.loads(redis_que.get())
                # print(unpacked[0]['vehicle_id'])

                asyncio.sleep(1)

    async def fetch_all_vehicle_data(self, session, url, params):
        async with async_timeout.timeout(settings.ASYNC_TIMEOUT_VALUE):
            async with session.get(url, params=params) as response:
                return await response.json()

    async def post_all_vehicle_data(self, session, url, all_adapted_vehicle_data):
        async with session.post(url, json=all_adapted_vehicle_data) as resp:
            print(await resp.text())

    def adapt_all_vehicle_data(self, all_vehicle_data) -> list:
        new_vehicle_data = []
        for vehicle_data in all_vehicle_data:
            new_vehicle_data.append(self.adapt_vehicle_data(vehicle_data))

        return new_vehicle_data

    def adapt_vehicle_data(self, vehicle_data) -> dict:
        return {'vehicle_id': vehicle_data['vehicle']['vehicle_id'],
                'vehicle': {'number': vehicle_data['vehicle']['license_plate'],
                            'type': vehicle_data['vehicle']['maker'] + " " + vehicle_data['vehicle']['model']},
                'position': {'latitude': vehicle_data['lat'],
                             'longitude': vehicle_data['lng'],
                             'moment': vehicle_data['moment']}
                }

    def _create_login_params(self) -> dict:
        timestamp = time.time()

        text = settings.SECRET_KEY + str(int(timestamp))
        signature = h.sha1(text.encode()).hexdigest()

        return {'client_id': settings.CLIENT_ID, 'timestamp': int(timestamp),
                'signature': signature}


class RedisQueue(object):
    """Simple Queue with Redis Backend"""
    def __init__(self, name, namespace='queue', **redis_kwargs):
        """The default connection parameters are: host='localhost', port=6379, db=0"""
        self.__db = redis.Redis(**redis_kwargs)
        self.key = '%s:%s'.format(namespace, name)

    def qsize(self):
        """Return the approximate size of the queue."""
        return self.__db.llen(self.key)

    def empty(self):
        """Return True if the queue is empty, False otherwise."""
        return self.qsize() == 0

    def put(self, item):
        """Put item into the queue."""
        self.__db.rpush(self.key, item)

    def get(self, block=True, timeout=None):
        """Remove and return an item from the queue.

        If optional args block is true and timeout is None (the default), block
        if necessary until an item is available."""
        if block:
            item = self.__db.blpop(self.key, timeout=timeout)
        else:
            item = self.__db.lpop(self.key)

        # if item:
        if block:
            item = item[1]

        return item

    def get_nowait(self):
        """Equivalent to get(False)."""
        return self.get(False)

