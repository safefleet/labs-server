from channels.generic.websocket import AsyncWebsocketConsumer
import json

class VehicleConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.vehicle_id = self.scope['url_route']['kwargs']['vehicle_id']
        self.vehicle_group_name = 'app_%s' % self.vehicle_id

        await self.accept()

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.send(
            self.vehicle_group_name,
            {
                'type': 'vehicle_id',
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def disconnect(self, close_code):
        pass
        # Called when the socket closes

