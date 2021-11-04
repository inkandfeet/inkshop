from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from products import views
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
    url(r'^refund/(?P<hashid>[0-9A-Za-z_\-]+)/$', views.refund, name='refund'),
    url(r'^refund-confirm/(?P<hashid>[0-9A-Za-z_\-]+)/$', views.refund_confirm, name='refund_confirm'),
    url(r'^today/$', views.today, name='today'),
    url(r'^favicon.ico$', website_views.favicon, name='favicon'),
    url(r'^purchase/config$', views.stripe_config, name='stripe_config'),
    url(r'^purchase/create-account$', views.create_account, name='create_account'),
    url(r'^webhook-endpoints/stripe$', views.stripe_webhook, name='stripe_webhook'),
    url(r'^account/$', views.account, name='account'),
    url(r'^account/confirm-delete/$', views.confirm_delete_account, name='confirm_delete_account'),
    url(r'^account-deleted/$', views.account_deleted, name='account_deleted'),
    url(r'^data_export/$', views.data_export, name='data_export'),
    url(r'^privacy/?$', views.privacy, name='privacy'),
    url(r'^bestimator/$', views.bestimator, name='bestimator'),
    url(r'^ra/?$', views.random_ad, name='random_ad'),
    url(r'^.well-known/apple-app-site-association/?$', views.apple_app_site_association, name='apple_app_site_association'),
    url(r'^apple-app-site-association/?$', views.apple_app_site_association, name='apple_app_site_association'),
    url(r'^bestimator/(?P<slug>[0-9A-Za-z_\-]+)/$', views.bestimator_experiment, name='bestimator_experiment'),
    url(r'^bestimator/(?P<slug>[0-9A-Za-z_\-]+)/save$', views.bestimator_save_feedback, name='bestimator_save_feedback'),
    url(r'^p/(?P<link>[0-9A-Za-z_\-=]+)/$', views.one_click_sign_in, name='one_click_sign_in'),
    url(r'^courses/(?P<url>.*)$', views.course_link_redirect, name='course_link_redirect'),
    url(r'^(?P<course_slug>[0-9A-Za-z_\-]+)/purchase/complete$', views.purchase_complete, name='purchase_complete'),
    url(r'^(?P<course_slug>[0-9A-Za-z_\-]+)/purchase/session$', views.create_checkout_session, name='create_checkout_session'),
    url(r'^(?P<course_slug>[0-9A-Za-z_\-]+)/purchase/help$', views.checkout_help_edition, name='checkout_help_edition'),
    url(r'^(?P<course_slug>[0-9A-Za-z_\-]+)/purchase/success$', views.checkout_success, name='checkout_success'),
    url(r'^(?P<course_slug>[0-9A-Za-z_\-]+)/purchase/cancelled$', views.checkout_cancelled, name='checkout_cancelled'),
    url(r'^(?P<course_slug>[0-9A-Za-z_\-]+)/download/(?P<resource_url>.*?)$', views.product_download, name='product_download'),
    url(r'^(?P<course_slug>[0-9A-Za-z_\-]+)/feedback$', views.send_feedback, name='send_feedback'),
    url(r'^(?P<course_slug>[0-9A-Za-z_\-]+)/beta/$', views.course_beta_purchase, name='course_beta_purchase'),
    url(r'^(?P<course_slug>[0-9A-Za-z_\-]+)/?$', views.course_purchase, name='course_purchase'),
]
