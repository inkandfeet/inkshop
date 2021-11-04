# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.views.static import serve

from . import views

urlpatterns = [
    url(r'^sitemap.xml$', views.sitemap, name='sitemap'),
    url(r'^favicon.ico$', views.favicon, name='favicon'),
    url(r'^privacy$', views.privacy, name='privacy'),
    url(r'^static/(?P<resource_slug>.*)$', views.resource, name='resource'),
    url(r'^(?P<page_slug>.*)$', views.page_or_post, name='page_or_post'),
    url(r'^$', views.page_or_post, name='root_page_or_post'),
]

if settings.DEBUG:
    urlpatterns += [
        url(
            r'^media/(?P<path>.*)$',
            serve, {
                'document_root': settings.MEDIA_ROOT,
            }
        ),
    ]
    urlpatterns += staticfiles_urlpatterns()
