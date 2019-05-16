from django.conf.urls import include, url
from django.contrib import admin
from people import views
from website import views as website_views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^auth$', views.user_authenticate, name='authenticate'),
    url(r'^auth/widget$', views.auth_widget, name='auth_widget'),
    url(r'^auth/signup$', views.user_signup, name='signup'),
    url(r'^auth/change-password$', views.change_password, name='change_password'),
    url(r'^auth/check-new-account$', views.check_new_account, name='check_new_account'),
    url(r'^reset-password$', views.reset_password, name='reset_password'),
    url(r'^auth/confirm-delete$', views.confirm_delete, name='confirm_delete'),
    url(r'^auth/confirm/(?P<email_key>[\w-]+)/?$', views.confirm_email, name='confirm_email'),
    url(r'^confirm-reset/(?P<email_key>[\w-]+)/$', views.confirm_reset, name='confirm_reset'),
    url(r'^favicon.ico$', website_views.favicon, name='favicon'),
]
