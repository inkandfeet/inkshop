from django.conf.urls import include, url
from django.contrib import admin
from products import views
from website import views as website_views

urlpatterns = [
    url(r'^$', views.home, name='home'),
]
