import json
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import WebsocketConsumer
from channels.auth import get_user
import channels.layers
from django.contrib.auth.signals import user_logged_in, user_logged_out 
from django.dispatch import receiver 
from products.models import JourneyDay



class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))


class JourneyDayConsumer(WebsocketConsumer):
    def connect(self):
        self.journey_hashid = self.scope['url_route']['kwargs']['journey_hashid']
        self.day_hashid = self.scope['url_route']['kwargs']['day_hashid']
        self.room_group_name = 'journey-day-%s-%s' % (self.journey_hashid, self.day_hashid)

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )


    # Receive message from WebSocket
    def receive(self, text_data):
        self.user = async_to_sync(get_user)(self.scope)
        print(self.user)
        print(self.user.is_authenticated)
        print(self.user.is_anonymous)
        text_data_json = json.loads(text_data)
        data = text_data_json['data']
        if not self.user.is_anonymous:
            print("logged in")
            # Send message to room group
            print(data)
            print("alive" in data)
            if "alive" in data and data["alive"]:
                return

            # Store in DB
            print(self.user)
            d = None
            try:
                d = JourneyDay.objects.get(hashid=self.day_hashid)
                print(d.journey.productpurchase.purchase.person)
                print(d.journey.productpurchase.purchase.person == self.user)
            except:
                pass
            print("d")
            print(d)
            # TODO: get this all fixed up.
            if d and d.journey.productpurchase.purchase.person == self.user:
                # , journey__productpurchase__person=self.user
                print("Valid user for this journeyday")
                print("hjourneyday")
                print(d)
                print(d.hashid)
                d.data = json.dumps(data)
                print(d.data)
                d.save()
    
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'data_update',
                        'data': data
                    }
                )

                return 

        
        print("unauthorized")
        print(data)
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'unauthorized',
                'data': {
                    'consumerguid': data.get('consumerguid', "")
                }
            }
        )

    # Receive message from room group
    def data_update(self, event):
        data = event['data']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': 'data_update',
            'data': data
        }))

    # Receive message from room group
    def unauthorized(self, event):
        data = event['data']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': 'unauthorized',
            'data': data
        }))
