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

    previous_vehicles_set = set()  # set that keeps the previous state of the vehicles
    vehicles_set = set()  # set that grabs data from the 1 per sec loop and keeps the current state of the vehicles

    previous_positions = []  # list that helps us to see if a location changed
    first_run = True

    def handle(self, *args, **options):
        loop = asyncio.get_event_loop()
        tasks = [asyncio.Task(self._main_locations()), asyncio.Task(self._main_vehicles())]
        loop.run_until_complete(asyncio.gather(*tasks))

    async def _main_vehicles(self):
        try:
            async with aiohttp.ClientSession() as session:

                channel_layer = channels.layers.get_channel_layer()

                while True:

                    if len(self.vehicles_set) > 0:  # wait for the current vehicles set to be filled
                        # check for new cars
                        new_vehicles_set = self.vehicles_set - self.previous_vehicles_set
                        # if there are any new cars post them
                        if len(new_vehicles_set) > 0:
                            # post
                            await self.post_all_vehicle_data(session, Vehicle.map_to_list_of_dicts(new_vehicles_set))
                            # redis
                            json_vehicle_data = json.dumps(Vehicle.map_to_list_of_dicts(new_vehicles_set))
                            await channel_layer.send(settings.CHANNEL_NAME_VEHICLES,
                                                     {'vehicle_data': json_vehicle_data})
                            # update reference set
                            self.previous_vehicles_set = set(self.vehicles_set)

                            print('New vehicles posted...')
                        else:
                            print('No vehicles updates..')

                    await asyncio.sleep(3600 * 10)  # sleep for 10 minutes

        except Exception as e:
            print('Problems with the source tool. Program is exiting...\nException: {}'.format(e))

    async def _main_locations(self):

        try:
            channel_layer = channels.layers.get_channel_layer()

            async with aiohttp.ClientSession() as session:
                while True:
                    # get
                    req_all_data = await self.fetch_all_vehicle_data(
                        session,
                        self._create_login_params())

                    # mapped dict
                    self.vehicles_set, new_position_data = self.adapt_all_data(req_all_data)
                    # tuple with (vehicle, position)

                    # post positions
                    await self.post_all_position_data(
                        session,
                        new_position_data)

                    # save to redis que as json
                    json_location_data = json.dumps(new_position_data)
                    await channel_layer.send(settings.CHANNEL_NAME_VEHICLES_LOCATION,
                                             {'location_data': json_location_data})

                    print('Running _main')
                    await asyncio.sleep(1)
        except Exception as e:
            print('Problems with the source tool. Program is exiting...\nException: {}'.format(e))

    async def fetch_all_vehicle_data(self, session, params):
        async with async_timeout.timeout(settings.ASYNC_TIMEOUT_VALUE):
            async with session.get(settings.SAFEFLEET_API_BASE_URL + '/get_current_positions',
                                   params=params) as response:
                return await response.json()

    async def post_all_vehicle_data(self, session, all_adapted_vehicle_data):
        await self.post_data(session, '/vehicles', all_adapted_vehicle_data)

    async def post_all_position_data(self, session, all_adapted_position_data):
        await self.post_data(session, '/positions', all_adapted_position_data)

    async def post_data(self, session, relative_url, data):
        async with session.post(settings.LABS_API_BASE_URL + relative_url, json=data) as resp:
            print('Response from url post: {}\n'.format(await resp.text))

    def adapt_all_data(self, all_vehicle_data) -> tuple:
        new_vehicle_data = set()  # vehicle class set
        new_position_data = []

        i = 0
        for vehicle_data in all_vehicle_data:
            new_data = self.adapt_data(vehicle_data)

            new_vehicle_data.add(new_data[0])

            if not self.first_run:
                if self._positions_changed(new_data[1], i):  # append only if the position changed
                    new_position_data.append(new_data[1])
            else:
                new_position_data.append(new_data[1])
                self.previous_positions.append(new_data[1])

            i += 1

        self.first_run = False  # after the first call of this function this param has to be false

        return new_vehicle_data, new_position_data

    def adapt_data(self, all_vehicle_data) -> tuple:  # (vehicle, position)
        return self.adapt_vehicle_data(all_vehicle_data), self.adapt_position_data(all_vehicle_data)

    def adapt_vehicle_data(self, all_vehicle_data):
        return Vehicle(all_vehicle_data['vehicle']['vehicle_id'],
                       {'vehicle': {'number': all_vehicle_data['vehicle']['license_plate'],
                                    'type': all_vehicle_data['vehicle']['maker'] + " " + all_vehicle_data['vehicle'][
                                        'model']}})

    def adapt_position_data(self, all_vehicle_data):
        return {'vehicle_id': all_vehicle_data['vehicle']['vehicle_id'],
                'position': {'latitude': all_vehicle_data['lat'],
                             'longitude': all_vehicle_data['lng'],
                             'moment': all_vehicle_data['moment']}
                }

    def _positions_changed(self, new_position, index):

        if index < len(self.previous_positions):
            if self.previous_positions[index]['position']['latitude'] != new_position['position']['latitude'] or self.previous_positions[index]['position']['longitude'] != new_position['position']['longitude']:
                # update the global list
                self.previous_positions[index]['position']['latitude'] = new_position['position']['latitude']
                self.previous_positions[index]['position']['longitude'] = new_position['position']['longitude']
                return True

            return False

        return True  # it means that the new position list is bigger than the old one -> it changed

    def _create_login_params(self) -> dict:
        timestamp = time.time()

        text = settings.SECRET_KEY_AUTH + str(int(timestamp))
        signature = h.sha1(text.encode()).hexdigest()

        return {'client_id': settings.CLIENT_ID, 'timestamp': int(timestamp),
                'signature': signature}


class Vehicle(object):

    def __init__(self, vehicle_id, data: dict):
        self.vehicle_id = vehicle_id
        self.data = data

    def to_dict(self) -> dict:
        self.data['vehicle_id'] = self.vehicle_id
        return self.data

    def __hash__(self):
        return self.vehicle_id.__hash__()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.vehicle_id == other.vehicle_id

        return False

    @staticmethod
    def map_to_list_of_dicts(set_of_vehicles):
        vehicles_list = []
        for vehicle in set_of_vehicles:
            vehicles_list.append(vehicle.to_dict())

        return vehicles_list

