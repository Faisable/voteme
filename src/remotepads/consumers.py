from email import message
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class Pad():
    def __init__(self, id, message) -> None:
        self.id = id
        self.rank = None
        self.message = message
    def __repr__(self) -> str:
        return self.id + " : " + str(self.rank)
    def __eq__(self, __o: object) -> bool:
        return self.id == __o.id

pads = []

class PadConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # self.room_name = self.scope['url_route']['kwargs']['room_name']
        #print(self.start)
        # print(self.room_name)
        # self.romm_group_name = 'chat_%s' % self.room_name
        self.romm_group_name = 'pads'
        # Joint le groupe
        await self.channel_layer.group_add(
            self.romm_group_name,
            self.channel_name
        )
        
        await self.accept()

       

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.romm_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None):
        text_data_json = json.loads(text_data)
        incoming = Pad(text_data_json['id'],text_data_json['message'])
        print('message %s' % incoming.message)
        if not incoming in pads and incoming.id != 'admin':
            pads.append(incoming)
            idx = pads.index(incoming)
            pads[idx].rank = idx + 1
        
        print(pads)
        await self.channel_layer.group_send(
            self.romm_group_name,
            {
                'type': 'chat_message',
                'message': text_data_json['message'],
                'id':text_data_json['id']
            }
        )
    async def chat_message(self, event):
        message = event['message']
        id = event['id']
        await self.send(text_data=json.dumps({
            'message': message,
            'id':id
        }))