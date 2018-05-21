from channels.generic.websocket import AsyncWebsocketConsumer
import json


class VehicleConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        vehicle_id = self.scope['url_route']['kwargs']['vehicle_id']
        self.room_name = 'positions_for_vehicle_%s' % vehicle_id

        # Join room group
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    # Receive message from room group
    async def vehicle_positions(self, event):
        message = event['position']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'position': message
        }))
