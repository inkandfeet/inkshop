from django.conf.urls import include, url
from django.contrib import admin
from . import views
from website import views as website_views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^subscribe/$', views.subscribe, name='subscribe'),
    url(
        r'^confirm-subscription/(?P<opt_in_key>[0-9A-Za-z_\-]+)/$',
        views.confirm_subscription,
        name='confirm_subscription'
    ),
    url(
        r'^transfer-subscription/(?P<transfer_code>[0-9A-Za-z_\-]+)/$',
        views.transfer_subscription,
        name='transfer_subscription'
    ),
    url(r'^unsubscribe/(?P<unsubscribe_key>[0-9A-Za-z_\-]+)/$', views.unsubscribe, name='unsubscribe'),
    url(r'^resubscribe/(?P<resubscribe_key>[0-9A-Za-z_\-]+)/$', views.resubscribe, name='resubscribe'),
    url(r'^delete-account/complete/$', views.delete_account_done, name='delete_account_done'),
    url(r'^delete-account/(?P<delete_key>[0-9A-Za-z_\-]+)/$', views.delete_account, name='delete_account'),
    url(r'^love/(?P<love_hash>[0-9A-Za-z_\-]+)/$', views.love_message, name='love_message'),
    url(r'^favicon.ico$', website_views.favicon, name='favicon'),
]
