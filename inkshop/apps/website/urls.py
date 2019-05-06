from django.conf.urls import include, url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^(?P<page_slug>.+)$', views.page_or_post, name='page_or_post'),
]
