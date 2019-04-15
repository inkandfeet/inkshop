import os
import sys
from os.path import join
from .common import *

ALLOWED_HOSTS += ["*", ]
COMPRESS_ENABLED = True
SESSION_COOKIE_DOMAIN = None

AWS_STORAGE_BUCKET_NAME = "inkandfeet-inkshop-dev"
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

if "INKSHOP_BASE_URL" in os.environ:
    MEDIA_URL = "%s/media/" % os.environ["INKSHOP_BASE_URL"]

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
