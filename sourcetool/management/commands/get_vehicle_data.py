from django.core.management.base import BaseCommand, CommandError
import time
import hashlib as h
from datetime import timedelta
import asyncio
import aiohttp
import async_timeout


class Command(BaseCommand):

    secret_key = '6LusIIpGX0APCp1ubE5EQXsfKRWubZSM'
    client_id = 'ligaac'
    async_timeout_value = 10

    def add_arguments(self, parser):
        # parser.add_argument('--show', action='store_true', dest='show')
        pass

    # def handle(self, *args, **options):
    #
    #     timestamp = time.time()
    #     params = {'client_id': self.client_id, 'timestamp': int(timestamp),
    #               'signature': self.create_signature(timestamp)}
    #
    #     while True:
    #
    #         if time.time() - timestamp >= timedelta(minutes=4.8).seconds:
    #             # signature expires after 5 minutes -> create new one with fresh timestamp
    #             # made it 4.8 minutes for safety purposes
    #             timestamp = time.time()
    #             params = {'client_id': self.client_id, 'timestamp': int(timestamp),
    #                       'signature': self.create_signature(timestamp)}
    #
    #         req = r.get('https://alpha.safefleet.eu/safefleet/api/get_current_positions', params=params)
    #
    #         if options['show']:
    #             print(req.json())
    #
    #         time.sleep(1)

    def handle(self, *args, **options):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._main())

    async def _main(self):

        timestamp = time.time()
        params = {'client_id': self.client_id, 'timestamp': int(timestamp),
                  'signature': self._create_signature(timestamp)}

        async with aiohttp.ClientSession() as session:
            while True:

                if time.time() - timestamp >= timedelta(minutes=4.8).seconds:
                    # signature expires after 5 minutes -> create new one with fresh timestamp
                    # made it 4.8 minutes for safety purposes
                    timestamp = time.time()
                    params = {'client_id': self.client_id, 'timestamp': int(timestamp),
                              'signature': self._create_signature(timestamp)}

                req_all_data = await self.fetch_json(session,
                                            'https://alpha.safefleet.eu/safefleet/api/get_current_positions',
                                            params)

                # demo code for unpacking the request
                i = 0
                for req in req_all_data:
                    print("Vehicle: {}".format(i))
                    print('Number: {}\nType: {}\nColor: {}\nLatitude: {}\nLongitute: {}\n'
                          .format(
                           req['vehicle']['vehicle_id'],
                           req['vehicle']['model'],
                           "DON'T KNOW",
                           req['lat'],
                           req['lng']
                           ))
                    i += 1

                asyncio.sleep(1)

    async def fetch_json(self, session, url, params):
        async with async_timeout.timeout(self.async_timeout_value):
            async with session.get(url, params=params) as response:
                return await response.json()

    def _create_signature(self, timestamp):
        text = self.secret_key + str(int(timestamp))
        return h.sha1(text.encode()).hexdigest()
