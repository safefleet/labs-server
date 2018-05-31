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

    LOGIN_CLIENT_ID = 'client_id'
    LOGIN_TIMESTAMP = 'timestamp'
    LOGIN_SIGNATURE = 'signature'

    API_VEHICLE_ID = 'vehicle_id'

    API_VEHICLE = 'vehicle'
    API_VEHICLE_NUMBER = 'number'
    API_VEHICLE_TYPE = 'type'

    API_POSITION = 'position'
    API_POSITION_LAT = 'lat'
    API_POSITION_LNG = 'lng'
    API_POSITION_MOMENT = 'moment'

    POST_VEHICLES_RELATIVE_URL = '/vehicles'
    POST_POSITION_RELATIVE_URL = '/positions'
    GET_ALL_DATA_RELATIVE_SAFEFLEET_URL = '/get_current_positions'

    CHANNEL_VEHICLE_DATA = 'vehicle_data'
    CHANNEL_LOCATION_DATA = 'location_data'

    previous_vehicles_set = set()  # set that keeps the previous state of the vehicles
    vehicles_set = set()  # set that grabs data from the 1 per sec loop and keeps the current state of the vehicles

    previous_positions = []  # list that helps us to see if a location changed

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
                                                     {self.CHANNEL_VEHICLE_DATA: json_vehicle_data})
                            # update reference set
                            self.previous_vehicles_set = set(self.vehicles_set)

                            print('New vehicles posted...')
                        else:
                            print('No vehicles updates..')

                        await asyncio.sleep(3600 * 10)  # sleep for 10 minutes
                    else:
                        await asyncio.sleep(10)

        except Exception as e:
            print('Problems with the vehicles source tool. Program is exiting...\nException: {}'.format(e))

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
                                             {self.CHANNEL_LOCATION_DATA: json_location_data})

                    print('Running _main')
                    await asyncio.sleep(1)
        except Exception as e:
            print('Problems with the location source tool. Program is exiting...\nException: {}'.format(e))

    async def fetch_all_vehicle_data(self, session, params):
        async with async_timeout.timeout(settings.ASYNC_TIMEOUT_VALUE):
            async with session.get(settings.SAFEFLEET_API_BASE_URL + self.GET_ALL_DATA_RELATIVE_SAFEFLEET_URL,
                                   params=params) as response:
                return await response.json()

    async def post_all_vehicle_data(self, session, all_adapted_vehicle_data):
        await self.post_data(session, self.POST_VEHICLES_RELATIVE_URL, all_adapted_vehicle_data)

    async def post_all_position_data(self, session, all_adapted_position_data):
        await self.post_data(session, self.POST_POSITION_RELATIVE_URL, all_adapted_position_data)

    async def post_data(self, session, relative_url, data):
        async with session.post(settings.LABS_API_BASE_URL + relative_url, json=data) as resp:
            print('Response from url post: {}\n'.format(await resp.text))

    def adapt_all_data(self, all_vehicle_data) -> tuple:
        new_vehicle_data = set()  # vehicle class set
        new_position_data = []

        for vehicle_data in all_vehicle_data:
            new_data = self.adapt_data(vehicle_data)

            new_vehicle_data.add(new_data[0])

            if self._positions_changed(new_data[1]):  # append only if the position changed
                new_position_data.append(new_data[1])

        print(self.previous_positions)
        print(new_position_data)
        return new_vehicle_data, new_position_data

    def adapt_data(self, all_vehicle_data) -> tuple:  # (vehicle, position)
        return self.adapt_vehicle_data(all_vehicle_data), self.adapt_position_data(all_vehicle_data)

    def adapt_vehicle_data(self, all_vehicle_data):
        return Vehicle(all_vehicle_data['vehicle']['vehicle_id'],
                       {self.API_VEHICLE: {self.API_VEHICLE_NUMBER: all_vehicle_data['vehicle']['license_plate'],
                                           self.API_VEHICLE_TYPE: all_vehicle_data['vehicle']['maker'] + " " +
                                                                  all_vehicle_data['vehicle'][
                                                                      'model']}})

    def adapt_position_data(self, all_vehicle_data):
        return {self.API_VEHICLE_ID: all_vehicle_data['vehicle']['vehicle_id'],
                self.API_POSITION: {self.API_POSITION_LAT: all_vehicle_data['lat'],
                                    self.API_POSITION_LNG: all_vehicle_data['lng'],
                                    self.API_POSITION_MOMENT: all_vehicle_data['moment']}
                }

    def _positions_changed(self, new_position):

        i = 0
        for prev_pos in self.previous_positions:
            if prev_pos[self.API_VEHICLE_ID] == new_position[self.API_VEHICLE_ID]:
                if prev_pos[self.API_POSITION][self.API_POSITION_LAT] != new_position[self.API_POSITION][self.API_POSITION_LAT] or prev_pos[self.API_POSITION][self.API_POSITION_LNG] != new_position[self.API_POSITION][self.API_POSITION_LNG]:
                    # update list
                    self.previous_positions[i][self.API_POSITION][self.API_POSITION_LAT] = new_position[self.API_POSITION][self.API_POSITION_LAT]
                    self.previous_positions[i][self.API_POSITION][self.API_POSITION_LNG] = new_position[self.API_POSITION][self.API_POSITION_LNG]
                    return True
                else:
                    return False
            i += 1

        # if it was not found it means that the position changed and it has to be added to the cached positions list
        self.previous_positions.append(new_position)
        return True

    def _create_login_params(self) -> dict:
        timestamp = time.time()

        text = settings.SECRET_KEY_AUTH + str(int(timestamp))
        signature = h.sha1(text.encode()).hexdigest()

        return {self.LOGIN_CLIENT_ID: settings.CLIENT_ID, self.LOGIN_TIMESTAMP: int(timestamp),
                self.LOGIN_SIGNATURE: signature}


class Vehicle(object):

    def __init__(self, vehicle_id, data: dict):
        self.vehicle_id = vehicle_id
        self.data = data

    def to_dict(self) -> dict:
        self.data[Command.API_VEHICLE_ID] = self.vehicle_id
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
