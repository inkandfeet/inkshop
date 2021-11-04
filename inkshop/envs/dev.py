import os
import sys
from os.path import join
from .common import *
try:
    from .secrets import *
except:
    pass

ALLOWED_HOSTS += ["*", ]
COMPRESS_ENABLED = True
SESSION_COOKIE_DOMAIN = None

AWS_STORAGE_BUCKET_NAME = "inkandfeet-inkshop-dev"
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
DEFAULT_FILE_STORAGE = 'utils.storage.InkshopFileStorage'

STATIC_PRECOMPILER_USE_CACHE = False
STATIC_PRECOMPILER_DISABLE_AUTO_COMPILE = True

if "INKSHOP_BASE_URL" in os.environ:
    MEDIA_URL = "%s/media/" % os.environ["INKSHOP_BASE_URL"]

# INSTALLED_APPS += ['debug_toolbar', ]

INTERNAL_IPS = [
    # ...
    '127.0.0.1',
    '172.18.0.5',
]
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': 'utils.middleware.show_toolbar_callback',
}
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
#     },
# }
redis_url = urlparse(BROKER_URL)
CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': '%s:%s' % (redis_url.hostname, redis_url.port),
        'OPTIONS': {
            'PASSWORD': redis_url.password,
            'DB': 0,
        }
    }
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
LOGIN_URL = "/accounts/login"
