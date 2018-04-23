from django.core.management.base import BaseCommand, CommandError
import requests as r
import time
import hashlib as h
from datetime import timedelta


class Command(BaseCommand):

    secret_key = '6LusIIpGX0APCp1ubE5EQXsfKRWubZSM'
    client_id = 'ligaac'

    def add_arguments(self, parser):
        parser.add_argument('--show', action='store_true', dest='show')

    def handle(self, *args, **options):

        timestamp = time.time()
        params = {'client_id': self.client_id, 'timestamp': int(timestamp),
                  'signature': self.create_signature(timestamp)}

        while True:

            if time.time() - timestamp >= timedelta(minutes=4.8).seconds:
                # signature expires after 5 minutes -> create new one with fresh timestamp
                # made it 4.8 minutes for safety purposes
                timestamp = time.time()
                params = {'client_id': self.client_id, 'timestamp': int(timestamp),
                          'signature': self.create_signature(timestamp)}

            req = r.get('https://alpha.safefleet.eu/safefleet/api/get_current_positions', params=params)

            if options['show']:
                print(req.json())

            time.sleep(1)

    def create_signature(self, timestamp):
        text = self.secret_key + str(int(timestamp))
        return h.sha1(text.encode()).hexdigest()
