from django.conf.urls import include, url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^subscribe/$', views.subscribe, name='subscribe'),
    url(r'^confirm-subscription/(?P<opt_in_key>[0-9A-Za-z_\-]+)/$', views.confirm_subscription, name='confirm_subscription'),
    url(r'^unsubscribe/(?P<unsubscribe_key>[0-9A-Za-z_\-]+)/$', views.unsubscribe, name='unsubscribe'),
    url(r'^delete-account/(?P<delete_key>[0-9A-Za-z_\-]+)/$', views.delete_account, name='delete_account'),
]
