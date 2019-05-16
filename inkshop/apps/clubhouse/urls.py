from django.conf.urls import include, url
from django.contrib import admin
from clubhouse import views
from website import views as website_views

urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^messages/$', views.messages, name='messages'),
    url(r'^messages/new/$', views.create_message, name='create_message'),
    url(r'^message/(?P<hashid>[0-9A-Za-z_\-]+)/$', views.message, name='message'),
    url(r'^posts/$', views.posts, name='posts'),
    url(r'^posts/new/$', views.create_post, name='create_post'),
    url(r'^post/(?P<hashid>[0-9A-Za-z_\-]+)/delete/$', views.delete_post, name='delete_post'),
    url(r'^post/(?P<hashid>[0-9A-Za-z_\-]+)/$', views.post, name='post'),
    url(r'^pages/$', views.pages, name='pages'),
    url(r'^pages/new/$', views.create_page, name='create_page'),
    url(r'^page/(?P<hashid>[0-9A-Za-z_\-]+)/delete/$', views.delete_page, name='delete_page'),
    url(r'^page/(?P<hashid>[0-9A-Za-z_\-]+)/$', views.page, name='page'),
    url(r'^templates/$', views.templates, name='templates'),
    url(r'^templates/new/$', views.create_template, name='create_template'),
    url(r'^template/(?P<hashid>[0-9A-Za-z_\-]+)/delete/$', views.delete_template, name='delete_template'),
    url(r'^template/(?P<hashid>[0-9A-Za-z_\-]+)/$', views.template, name='template'),
    url(r'^resources/$', views.resources, name='resources'),
    url(r'^resources/new/$', views.create_resource, name='create_resource'),
    url(r'^resource/(?P<hashid>[0-9A-Za-z_\-]+)/delete/$', views.delete_resource, name='delete_resource'),
    url(r'^resource/(?P<hashid>[0-9A-Za-z_\-]+)/$', views.resource, name='resource'),
    url(r'^links/$', views.links, name='links'),
    url(r'^links/new/$', views.create_link, name='create_link'),
    url(r'^link/(?P<hashid>[0-9A-Za-z_\-]+)/delete/$', views.delete_link, name='delete_link'),
    url(r'^link/(?P<hashid>[0-9A-Za-z_\-]+)/$', views.link, name='link'),
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
    url(r'^favicon.ico$', website_views.favicon, name='favicon'),
]
