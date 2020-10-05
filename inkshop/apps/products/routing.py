from django.urls import re_path

from products import consumers

websocket_urlpatterns = [
    # re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer),
    re_path(r'ws/journey/(?P<journey_hashid>[0-9A-Za-z_\-]+)/(?P<day_hashid>[0-9A-Za-z_\-]+)$', consumers.JourneyDayConsumer),
    re_path(r'ws/p/(?P<person_hashid>[0-9A-Za-z_\-]+)$', consumers.PersonConsumer),
]
