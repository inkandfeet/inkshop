from django.conf.urls import include, url
from django.contrib import admin
from clubhouse import views

urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^messages/$', views.messages, name='messages'),
    url(r'^message/(?P<hashid>[0-9A-Za-z_\-]+)/$', views.message, name='message'),
    url(r'^people/$', views.people, name='people'),
    url(r'^person/(?P<hashid>[0-9A-Za-z_\-]+)/$', views.person, name='person'),
    url(r'^newsletters/$', views.newsletters, name='newsletters'),
    url(r'^newsletter/(?P<hashid>[0-9A-Za-z_\-]+)/$', views.newsletter, name='newsletter'),
    url(r'^scheduled_newsletters/$', views.scheduled_newsletters, name='scheduled_newsletters'),
    url(r'^scheduled_newsletter/(?P<hashid>[0-9A-Za-z_\-]+)/$', views.scheduled_newsletter, name='scheduled_newsletter'),  # noqa
]
