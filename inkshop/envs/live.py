import os
try:
    from urllib.parse import urlparse
except:
    from urlparse import urlparse
# from memcacheify import memcacheify
from postgresify import postgresify
from .common import *


DEBUG = False
TEMPLATE_DEBUG = DEBUG
IS_LIVE = True

SESSION_COOKIE_DOMAIN = INKSHOP_DOMAIN
SESSION_COOKIE_NAME = "%s_id" % INKSHOP_NAMESPACE
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
CORS_ORIGIN_WHITELIST = (
    INKSHOP_DOMAIN,
    'http://localhost',
    'https://localhost',
)

SESSION_COOKIE_SECURE = True

ANYMAIL = {
    "MAILGUN_API_KEY": MAILGUN_API_KEY,
    "MAILGUN_SENDER_DOMAIN": MAILGUN_SENDER_DOMAIN,
}
EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"


# Handle Stunnel
# https://devcenter.heroku.com/articles/securing-heroku-redis
if "REDIS_URL_STUNNEL" in os.environ:
    STUNNELED_URL = os.environ["REDIS_URL_STUNNEL"]
else:
    base_redis_url_parts = os.environ["REDIS_URL"].split(":")
    stunnel_port = int(base_redis_url_parts[-1]) + 1
    base_redis_url_parts[-1] = str(stunnel_port)

    STUNNELED_URL = ":".join(base_redis_url_parts)

BROKER_URL = STUNNELED_URL
CELERY_BROKER_URL = STUNNELED_URL

# AWS_S3_CALLING_FORMAT = 'boto.s3.connection.OrdinaryCallingFormat'
AWS_DEFAULT_ACL = "public-read"
AWS_S3_CUSTOM_DOMAIN = AWS_STORAGE_BUCKET_NAME
MEDIA_URL = 'https://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
STATIC_URL = 'https://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME


FAVICON_URL = "%sfavicon.ico" % STATIC_URL

redis_url = urlparse(os.environ.get('REDIS_URL'))
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


DATABASES = None
DATABASES = postgresify()
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = DEFAULT_FILE_STORAGE
COMPRESS_STORAGE = STATICFILES_STORAGE
COMPRESS_URL = STATIC_URL
RESOURCES_URL = "https://%s/static/" % INKSHOP_DOMAIN

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True

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
            'handlers': ['mail_admins', ],
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
