import json
from time import sleep

from asgiref.sync import async_to_sync
from django.core.management.base import BaseCommand
from channels import layers


class Command(BaseCommand):
    help = 'It generates some fake location data'

    def handle(self, *args, **options):
        channel_layer = layers.get_channel_layer()

        positions = json.load(open('vehicle/positions.json'))

        while True:
            for position in positions:
                async_to_sync(channel_layer.group_send)(
                    'positions_for_vehicle_1',
                    {'type': 'vehicle_positions', 'position': position}
                )

                self.stdout.write(self.style.SUCCESS('Sent: {}'.format(position)))

                sleep(1)

            sleep(5)
