import hashlib as h
import asyncio
import aiohttp
import channels.layers
import logging

import async_timeout
import time

import json

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    LOGIN_CLIENT_ID = 'client_id'
    LOGIN_TIMESTAMP = 'timestamp'
    LOGIN_SIGNATURE = 'signature'

    LABS_LOGIN_USERNAME = 'username'
    LABS_LOGIN_PASSWORD = 'password'
    LABS_LOGIN_EMAIL = 'email'

    JWT_KEY = 'Authorization'
    JWT_VALUE_IDENTIFIER = 'JWT '

    API_VEHICLE_ID = 'id'
    API_VEHICLE = 'vehicle'
    API_VEHICLE_NUMBER = 'number'
    API_VEHICLE_TYPE = 'type'
    API_VEHICLE_COLOR = 'color'

    API_POSITION = 'position'
    API_POSITION_LAT = 'latitude'
    API_POSITION_LNG = 'longitude'
    API_POSITION_MOMENT = 'moment'

    # labs server relative urls
    POST_VEHICLES_RELATIVE_URL = '/api/vehicles/'
    GET_VEHICLES_RELATIVE_URL = '/api/vehicles/'
    GET_TOKEN_RELATIVE_URL = '/api-token-auth/'
    GET_JOURNEYS_FOR_VEHICLE_RELATIVE_URL = GET_VEHICLES_RELATIVE_URL + '{}/journeys/'
    POST_JOURNEYS_FOR_VEHICLE_RELATIVE_URL = POST_VEHICLES_RELATIVE_URL + '{}/journeys/'
    POST_POSITION_RELATIVE_URL = POST_JOURNEYS_FOR_VEHICLE_RELATIVE_URL + '{}/positions/'

    # safefleet server relative urls
    GET_ALL_DATA_RELATIVE_SAFEFLEET_URL = '/get_current_positions'

    CHANNEL_VEHICLE_DATA = 'vehicle_data'
    CHANNEL_LOCATION_DATA = 'location_data'

    ASYNC_TIMEOUT_VALUE = 100
    NO_JOURNEY = -1

    token = ""

    previous_vehicles_set = set()  # set that keeps the previous state of
    # the vehicles and will be initialized with the data in the labs server
    vehicles_set = set()  # set that grabs data from the 1 per sec loop and keeps the current state of the vehicles

    previous_positions = []  # list that helps us to see if a location changed
    vehicles_current_journeys = dict()  # dict that will keep for all
    # the current vehicles their current journey from the labs server ( vehicle_id -> journey_id)

    start_vehicles_loop = False  # the _main_vehicles loop can't start until some preparations
    # are done in the _main_locations loop

    def handle(self, *args, **options):
        loop = asyncio.get_event_loop()
        tasks = [asyncio.Task(self._main_locations()), asyncio.Task(self._main_vehicles())]
        loop.run_until_complete(asyncio.gather(*tasks))

    async def _main_vehicles(self):
        try:
            channel_layer = channels.layers.get_channel_layer()
            while True:
                if self.start_vehicles_loop:
                    # wait for the current vehicles set to be filled and the token to be grabbed

                    await self.check_for_new_cars(channel_layer)

                    await asyncio.sleep(3600 * 10)  # sleep for 10 minutes
                else:
                    await asyncio.sleep(10)
        except Exception:
            logging.error(' Problems with the vehicles source tool. Program is exiting...\n', exc_info=True)

    async def _main_locations(self):

        try:
            channel_layer = channels.layers.get_channel_layer()

            self.token = await self.get_from_labs_jwt()  # get token from labs server
            self.previous_vehicles_set = await self.get_from_labs_vehicles()
            # start the reference system with the data from the labs server

            # get all data from safefleet server
            req_all_data = await self.fetch_all_vehicle_data(
                self._create_login_params())
            # adapt the data from the safefleet server
            self.vehicles_set, new_position_data = self.adapt_all_data(req_all_data)
            # tuple with (vehicle, position)

            await self.check_for_new_cars(channel_layer)  # synchronize vehicles with the safefleet server

            self.vehicles_current_journeys = await self.get_from_labs_current_journeys()
            # fill the dict with the current journeys ( vehicle_id -> journey_id)

            # post positions ( it is important to post the positions here too,
            # cuz in the  self.adapt_all_data() the reference positions list it is filled and at the next call
            # the positions that are not changed will not be added to the new_position_data list)
            for position in new_position_data:
                await self.post_position_data(
                    position[self.API_POSITION],
                    position[self.API_VEHICLE_ID])

            # save to redis que as json
            json_location_data = json.dumps(new_position_data)
            await channel_layer.send(settings.CHANNEL_NAME_VEHICLES_LOCATION,
                                     {self.CHANNEL_LOCATION_DATA: json_location_data})

            self.start_vehicles_loop = True  # all the synchronization is done so the vehicles loop can start

            while True:
                # get
                req_all_data = await self.fetch_all_vehicle_data(
                    self._create_login_params())

                # mapped dict
                self.vehicles_set, new_position_data = self.adapt_all_data(req_all_data)
                # tuple with (vehicle, position)

                # post positions
                for position in new_position_data:
                    await self.post_position_data(
                        position[self.API_POSITION],
                        position[self.API_VEHICLE_ID])

                # save to redis que as json
                json_location_data = json.dumps(new_position_data)
                await channel_layer.send(settings.CHANNEL_NAME_VEHICLES_LOCATION,
                                         {self.CHANNEL_LOCATION_DATA: json_location_data})

                print('Running _main')
                await asyncio.sleep(1)
        except Exception:
            logging.error(' Problems with the location source tool. Program is exiting...\n', exc_info=True)

    async def check_for_new_cars(self, channel_layer):
        new_vehicles_set = self.vehicles_set - self.previous_vehicles_set

        # if there are any new cars post them
        if len(new_vehicles_set) > 0:

            # post new vehicles and cache journey references
            for vehicle in new_vehicles_set:
                await self.post_vehicle_data(vehicle.to_dict())
                self.vehicles_current_journeys[vehicle.vehicle_id] = \
                    await self.get_from_labs_current_journey_id(vehicle.vehicle_id)

            # redis
            json_vehicle_data = json.dumps(Vehicle.map_to_list_of_dicts(new_vehicles_set))
            await channel_layer.send(settings.CHANNEL_NAME_VEHICLES,
                                     {self.CHANNEL_VEHICLE_DATA: json_vehicle_data})

            # update reference set
            self.previous_vehicles_set = set(self.vehicles_set)
            print('New vehicles posted...')
        else:
            print('No vehicles updates..')

    async def fetch_all_vehicle_data(self, params):
        async with aiohttp.ClientSession() as session:
            async with async_timeout.timeout(self.ASYNC_TIMEOUT_VALUE):
                async with session.get(settings.SAFEFLEET_API_BASE_URL + self.GET_ALL_DATA_RELATIVE_SAFEFLEET_URL,
                                       params=params) as response:
                    return await response.json()

    async def get_from_labs_current_journeys(self) -> dict:
        journeys = dict()
        for vehicle in self.previous_vehicles_set:
            journeys[vehicle.vehicle_id] = await self.get_from_labs_current_journey_id(vehicle.vehicle_id)

        return journeys

    async def get_from_labs_current_journey_id(self, vehicle_id):
        journeys = await self.get_from_labs(
            self.GET_JOURNEYS_FOR_VEHICLE_RELATIVE_URL.format(vehicle_id), dict())

        try:
            if len(journeys) == 0 or journeys['detail'] == 'Not found':
                # it means that there is no journey so we have to create one
                await self.post_journey(vehicle_id)
                return self.get_from_labs_current_journey_id(vehicle_id)
                # retry to get the journey with the same logic
            else:
                return self.get_current_active_journey(journeys)
        except TypeError:
            return self.get_current_active_journey(journeys)

    def get_current_active_journey(self, journeys):
        max_id = self.NO_JOURNEY
        # consider that the biggest journey id is the current journey for that specific vehicle

        for journey in journeys:
            if journey['id'] > max_id:
                max_id = journey['id']

        return max_id

    async def get_from_labs_vehicles(self) -> set:
        vehicle_set = set()
        data = await self.get_from_labs(self.GET_VEHICLES_RELATIVE_URL, dict())
        for vehicle in data:
            vehicle_set.add(Vehicle(vehicle[self.API_VEHICLE_ID], vehicle))

        return vehicle_set

    async def get_from_labs_jwt(self) -> str:
        resp = await self.post_data(self.GET_TOKEN_RELATIVE_URL, {self.LABS_LOGIN_USERNAME: settings.USERNAME,
                                                                  self.LABS_LOGIN_PASSWORD: settings.PASSWORD,
                                                                  self.LABS_LOGIN_EMAIL: settings.EMAIL}, "JWT token")
        return resp['token']

    async def get_from_labs(self, relative_url, params):
        async with aiohttp.ClientSession() as session:
            async with async_timeout.timeout(self.ASYNC_TIMEOUT_VALUE):
                async with session.get(settings.LABS_API_BASE_URL + relative_url,
                                       json=params, headers=self._create_jwt_header()) as response:
                    return await response.json()

    async def post_journey(self, vehicle_id):
        await self.post_data(self.POST_JOURNEYS_FOR_VEHICLE_RELATIVE_URL.format(vehicle_id), dict(), "Journey data")

    async def post_vehicle_data(self, adapted_vehicle_data):
        await self.post_data(self.POST_VEHICLES_RELATIVE_URL, adapted_vehicle_data, "Vehicle data")

    async def post_position_data(self, adapted_position_data, vehicle_id):
        
        if vehicle_id in self.vehicles_current_journeys and self.vehicles_current_journeys[vehicle_id] != self.NO_JOURNEY:
            await self.post_data(
                self.POST_POSITION_RELATIVE_URL.format(vehicle_id,
                                                       self.vehicles_current_journeys[vehicle_id]),
                adapted_position_data, "Position data")

    async def post_data(self, relative_url, data, message):
        async with aiohttp.ClientSession() as session:
            async with session.post(settings.LABS_API_BASE_URL + relative_url,
                                    json=data, headers=self._create_jwt_header()) as resp:
                data = await resp.json()
                print('{} -> post: {}\n'.format(message, data))
                return data

    def adapt_all_data(self, all_vehicle_data) -> tuple:
        new_vehicle_data = set()  # vehicle class set
        new_position_data = []

        for vehicle_data in all_vehicle_data:
            new_data = self.adapt_data(vehicle_data)

            new_vehicle_data.add(new_data[0])

            if self._positions_changed(new_data[1]):  # append only if the position changed
                new_position_data.append(new_data[1])

        return new_vehicle_data, new_position_data

    def adapt_data(self, vehicle_data) -> tuple:  # (vehicle, position)
        return self.adapt_vehicle_data(vehicle_data), self.adapt_position_data(vehicle_data)

    def adapt_vehicle_data(self, vehicle_data):
        return Vehicle(vehicle_data['vehicle']['vehicle_id'],
                       {self.API_VEHICLE: {self.API_VEHICLE_NUMBER: vehicle_data['vehicle']['license_plate'],
                                           self.API_VEHICLE_TYPE: vehicle_data['vehicle']['maker'] + " " +
                                                                  vehicle_data['vehicle'][
                                                                      'model'],
                                           self.API_VEHICLE_COLOR: 'None'}})

    def adapt_position_data(self, vehicle_data):
        return {self.API_VEHICLE_ID: vehicle_data['vehicle']['vehicle_id'],
                self.API_POSITION: {self.API_VEHICLE_ID: vehicle_data['vehicle']['vehicle_id'],
                                    self.API_POSITION_LAT: vehicle_data['lat'],
                                    self.API_POSITION_LNG: vehicle_data['lng'],
                                    self.API_POSITION_MOMENT: vehicle_data['moment']}
                }

    def _positions_changed(self, new_position):

        i = 0
        for prev_pos in self.previous_positions:
            if prev_pos[self.API_VEHICLE_ID] == new_position[self.API_VEHICLE_ID]:
                if prev_pos[self.API_POSITION][self.API_POSITION_LAT] != new_position[self.API_POSITION][
                    self.API_POSITION_LAT] or prev_pos[self.API_POSITION][self.API_POSITION_LNG] != \
                        new_position[self.API_POSITION][self.API_POSITION_LNG]:
                    # update list
                    self.previous_positions[i][self.API_POSITION][self.API_POSITION_LAT] = \
                        new_position[self.API_POSITION][self.API_POSITION_LAT]
                    self.previous_positions[i][self.API_POSITION][self.API_POSITION_LNG] = \
                        new_position[self.API_POSITION][self.API_POSITION_LNG]
                    return True
                else:
                    return False
            i += 1

        # if it was not found it means that the position changed and it has to be added to the cached positions list
        self.previous_positions.append(new_position)
        return True

    def _create_jwt_header(self) -> dict:
        if self.token is not "":
            return {self.JWT_KEY: '{}{}'.format(self.JWT_VALUE_IDENTIFIER, self.token)}
        else:
            return dict()

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
        self.data[Command.API_VEHICLE][Command.API_VEHICLE_ID] = self.vehicle_id
        return self.data[Command.API_VEHICLE]

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
