from django.conf.urls import include, url
from django.urls import path, re_path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.views.static import serve

urlpatterns = [

    url(r'^admin/password_reset/$', auth_views.PasswordResetView, name='admin_password_reset'),
    url(r'^admin/password_reset/done/$', auth_views.PasswordResetDoneView, name='password_reset_done'),
    url(r'^accounts/login/$', auth_views.LoginView),
    url(
        r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        auth_views.PasswordResetConfirmView,
        name='password_reset_confirm'
    ),
    url(r'^reset/done/$', auth_views.PasswordResetCompleteView, name='password_reset_complete'),
    url(r'^$', include(('website.urls', 'website'), namespace="website")),
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
