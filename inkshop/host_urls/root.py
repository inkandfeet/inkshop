from django.conf.urls import include, url
from django.urls import path, re_path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    url(r'^mail/', include(('inkmail.urls', 'inkmail'), namespace="inkmail")),
    url(r'^clubhouse/', include(('clubhouse.urls', 'clubhouse'), namespace="clubhouse")),
    url(r'^website/', include(('website.urls', 'website'), namespace="website")),
    url(r'^draft/', include(('website.urls', 'website'), namespace="draft")),

    url(r'^admin/password_reset/$', auth_views.PasswordResetView, name='admin_password_reset'),
    url(r'^admin/password_reset/done/$', auth_views.PasswordResetDoneView, name='password_reset_done'),

    url(r'^accounts/login/$', auth_views.LoginView.as_view(), {'template_name': 'login.html', }, name='login'),
    url(r'^accounts/logout/$', auth_views.LogoutView.as_view(), {'next_page': '/'}, name='logout'),

    url(
        r'^accounts/password-reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),
    url(r'^accounts/password-reset/done/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
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
