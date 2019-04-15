from django.conf.urls import include, url
from django.urls import path, re_path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    url(r'^$', include(('dots.urls', 'dots'), namespace="dots")),
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
