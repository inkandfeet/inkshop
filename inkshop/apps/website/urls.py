from django.conf.urls import include, url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^static/(?P<resource_slug>.*)$', views.resource, name='resource'),
    url(r'^(?P<page_slug>.*)$', views.page_or_post, name='page_or_post'),
    url(r'^$', views.page_or_post, name='root_page_or_post'),
]
