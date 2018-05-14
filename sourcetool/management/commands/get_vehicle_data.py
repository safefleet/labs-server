import hashlib as h
import asyncio
import aiohttp
import channels.layers

import async_timeout
import time

import json

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):

    def handle(self, *args, **options):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._main())

    async def _main(self):

        channel_layer = channels.layers.get_channel_layer()

        async with aiohttp.ClientSession() as session:
            while True:

                # get
                req_all_data = await self.fetch_all_vehicle_data(
                    session,
                    'https://alpha.safefleet.eu/safefleet/api/get_current_positions',
                    self._create_login_params())

                # mapped dict
                new_vehicle_data, new_position_data = self.adapt_all_data(req_all_data)
                # tuple with (vehicle, position) class

                # TODO add desired urls
                # post
                # await self.post_all_vehicle_data(
                #     session,
                #     'url',
                #     new_vehicle_data)  # post vehicles

                await self.post_all_position_data(
                    session,
                    'http://127.0.0.1:8000/sourcetool/',
                    new_position_data)  # post positions

                # save to redis que as json
                json_vehicle_data = json.dumps(new_vehicle_data)
                json_location_data = json.dumps(new_position_data)
                await channel_layer.send(settings.CHANNEL_NAME, {settings.JSON_DATA_VEHICLES_KEY: json_vehicle_data,
                                                                 settings.JSON_DATA_LOCATIONS_KEY: json_location_data})

                asyncio.sleep(1)

    async def fetch_all_vehicle_data(self, session, url, params):
        async with async_timeout.timeout(settings.ASYNC_TIMEOUT_VALUE):
            async with session.get(url, params=params) as response:
                return await response.json()

    async def post_all_vehicle_data(self, session, url, all_adapted_vehicle_data):
        async with session.post(url, json=all_adapted_vehicle_data) as resp:
            print('Response from vehicles post:\n {}'.format(await resp.text()))

    async def post_all_position_data(self, session, url, all_adapted_position_data):
        async with session.post(url, json=all_adapted_position_data) as resp:
            print('Response from position post:\n {}'.format(await resp.text()))

    def adapt_all_data(self, all_vehicle_data) -> tuple:
        new_vehicle_data = []
        new_position_data = []

        for vehicle_data in all_vehicle_data:
            new_data = self.adapt_data(vehicle_data)

            new_vehicle_data.append(new_data[0])
            new_position_data.append(new_data[1])

        return new_vehicle_data, new_position_data

    def adapt_data(self, vehicle_data) -> tuple:  # (vehicle, position)
        return ({'vehicle_id': vehicle_data['vehicle']['vehicle_id'],
                 'vehicle': {'number': vehicle_data['vehicle']['license_plate'],
                             'type': vehicle_data['vehicle']['maker'] + " " + vehicle_data['vehicle']['model']}
                 },
                {'vehicle_id': vehicle_data['vehicle']['vehicle_id'],
                 'position': {'latitude': vehicle_data['lat'],
                              'longitude': vehicle_data['lng'],
                              'moment': vehicle_data['moment']}
                 }
                )

    def _create_login_params(self) -> dict:
        timestamp = time.time()

        text = settings.SECRET_KEY_AUTH + str(int(timestamp))
        signature = h.sha1(text.encode()).hexdigest()

        return {'client_id': settings.CLIENT_ID, 'timestamp': int(timestamp),
                'signature': signature}
