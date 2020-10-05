from django.conf.urls import include, url
from django.contrib import admin
from products import views
from django.contrib.auth import views as auth_views
from website import views as website_views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^ca/$', views.check_login, name='check_login'),
    url(r'^course/(?P<hashid>[0-9A-Za-z_\-]+)/$', views.productpurchase, name='productpurchase'),
    url(r'^journey/(?P<hashid>[0-9A-Za-z_\-]+)/$', views.journey, name='journey'),
    url(r'^start-journey/(?P<hashid>[0-9A-Za-z_\-]+)/$', views.start_journey, name='start_journey'),
    url(r'^delete-journey/(?P<hashid>[0-9A-Za-z_\-]+)/$', views.confirm_delete_journey, name='confirm_delete_journey'),
    url(r'^delete-journey-confirmed/(?P<hashid>[0-9A-Za-z_\-]+)/$', views.delete_journey, name='delete_journey'),
    url(r'^day/(?P<hashid>[0-9A-Za-z_\-]+)/$', views.day, name='day'),
    url(r'^today/$', views.today, name='today'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), {'next_page': '/'}, name='logout'),
]
