from django.conf.urls import include, url
from django.contrib import admin
from clubhouse import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
]
