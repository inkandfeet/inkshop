from django.conf.urls import include, url
from django.urls import path, re_path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.views.static import serve
from utils.auth import InkshopPasswordResetView


urlpatterns = [

    url(r'^accounts/password_reset/$', InkshopPasswordResetView.as_view(), name='password_reset'),
    url(r'^accounts/password_reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(r'^accounts/login/$', auth_views.LoginView.as_view(), {'template_name': 'login.html', }, name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), {'next_page': '/'}, name='logout'),

    url(
        r'^accounts/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),
    url(r'^accounts/reset/done/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    url(r'^', include(('products.urls', 'products'), namespace="products")),
    url(r'^', include(('website.urls', 'website'), namespace="website")),
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
