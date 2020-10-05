import json
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import WebsocketConsumer
from channels.auth import get_user
import channels.layers
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from products.models import JourneyDay
from people.models import Person


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
        text_data_json = json.loads(text_data)
        data = text_data_json['data']
        if not self.user.is_anonymous:
            if "alive" in data and data["alive"]:
                return

            # Store in DB
            d = None
            try:
                d = JourneyDay.objects.get(hashid=self.day_hashid)
            except:
                pass

            if d and d.journey.productpurchase.purchase.person == self.user:
                d.data = json.dumps(data)
                d.last_user_action = timezone.now()
                d.save()

                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'data_update',
                        'data': data
                    }
                )

                return

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


class PersonConsumer(WebsocketConsumer):
    def connect(self):
        self.person_hashid = self.scope['url_route']['kwargs']['person_hashid']
        self.room_group_name = 'p-%s' % (self.person_hashid,)

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
        text_data_json = json.loads(text_data)
        data = text_data_json['data']

        if not self.user.is_anonymous:
            if "alive" in data and data["alive"]:
                return

            p = None
            try:
                p = Person.objects.get(hashid=self.person_hashid)
            except:
                import traceback
                traceback.print_exc()
                pass

            if p and p == self.user:
                p.data = json.dumps(data)
                p.save()

                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'data_update',
                        'data': data
                    }
                )

                return

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
