from django.conf.urls import include, url
from django.contrib import admin
from clubhouse import views

urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^messages/$', views.messages, name='messages'),
    url(r'^messages/new/$', views.create_message, name='create_message'),
    url(r'^message/(?P<hashid>[0-9A-Za-z_\-]+)/$', views.message, name='message'),
    url(r'^people/$', views.people, name='people'),
    url(r'^organization/$', views.organization, name='organization'),
    url(r'^person/(?P<hashid>[0-9A-Za-z_\-]+)/$', views.person, name='person'),
    url(r'^subscriptions/$', views.subscriptions, name='subscriptions'),
    url(r'^subscription/(?P<hashid>[0-9A-Za-z_\-]+)/$', views.subscription, name='subscription'),
    url(r'^newsletters/$', views.newsletters, name='newsletters'),
    url(r'^newsletters/new/$', views.create_newsletter, name='create_newsletter'),
    url(r'^newsletter/(?P<hashid>[0-9A-Za-z_\-]+)/$', views.newsletter, name='newsletter'),
    url(r'^scheduled_newsletter_messages/$', views.scheduled_newsletter_messages, name='scheduled_newsletter_messages'),
    url(
        r'^scheduled_newsletter_messages/new$',
        views.create_scheduled_newsletter_message,
        name='create_scheduled_newsletter_message'
    ),
    url(
        r'^scheduled_newsletter_message/(?P<hashid>[0-9A-Za-z_\-]+)/$',
        views.scheduled_newsletter_message,
        name='scheduled_newsletter_message'
    ),
    url(
        r'^scheduled_newsletter_message/(?P<hashid>[0-9A-Za-z_\-]+)/queue/$',
        views.scheduled_newsletter_message_confirm_queue,
        name='scheduled_newsletter_message_confirm_queue'
    ),
    url(
        r'^scheduled_newsletter_message/(?P<hashid>[0-9A-Za-z_\-]+)/queue-confirm/$',
        views.scheduled_newsletter_message_queued,
        name='scheduled_newsletter_message_queued'
    ),
]
