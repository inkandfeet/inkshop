import logging
import os
import sys
from os.path import abspath, join, dirname
from sys import path

from .configure import *


PROJECT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
BASE_DIR = os.path.join(PROJECT_DIR, "..")
APPS_DIR = os.path.join(PROJECT_DIR, "apps")
path.insert(0, BASE_DIR)
path.insert(0, PROJECT_DIR)
path.insert(0, APPS_DIR)


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


ADMINS = (
    (INKSHOP_ADMIN_NAME, INKSHOP_ADMIN_EMAIL),
)
MANAGERS = ADMINS

ANYMAIL = {
    "MAILGUN_API_KEY": MAILGUN_API_KEY,
    "MAILGUN_SENDER_DOMAIN": MAILGUN_SENDER_DOMAIN,
}
EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"


DEV_SETUP = False
SESSION_EXPIRES_AFTER_SECONDS = 30 * 60  # 30 minutes

EMAIL_SUBJECT_PREFIX = "%s " % INKSHOP_FRIENDLY_NAME
DEFAULT_FROM_EMAIL = '%s <%s>' % (INKSHOP_FRIENDLY_NAME, INKSHOP_FROM_EMAIL)
SERVER_EMAIL = DEFAULT_FROM_EMAIL

CONFIRM_BASE_URL = INKSHOP_BASE_URL.replace("://", "://confirm.")
DRAFT_BASE_URL = INKSHOP_BASE_URL.replace("://", "://draft.")
ALLOWED_HOSTS = [
    INKSHOP_BASE_URL,
    DRAFT_BASE_URL,
    CONFIRM_BASE_URL,
    INKSHOP_BASE_URL.replace("://", "://mail."),
    INKSHOP_BASE_URL.replace("://", "://heart."),
    INKSHOP_BASE_URL.replace("://", "://dots."),
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',

    'anymail',
    'corsheaders',
    'compressor',
    'django_celery_beat',
    'django_celery_results',

    'inkdots',
    'inkmail',
    'people',
    'website',
    'utils',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'inkshop.wsgi.application'

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'redis:6379',
        'OPTIONS': {
            'DB': 0,
        }
    }
}

MIDDLEWARE = (
    'corsheaders.middleware.CorsMiddleware',
    'django_hosts.middleware.HostsRequestMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'htmlmin.middleware.HtmlMinifyMiddleware',
    'htmlmin.middleware.MarkRequestMiddleware',
    'django_hosts.middleware.HostsResponseMiddleware',
)

ROOT_URLCONF = 'inkshop.urls'
ROOT_HOSTCONF = 'inkshop.hosts'
DEFAULT_HOST = 'root'
SITE_ID = 1

# AUTH_USER_MODEL = 'people.User'

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_SAVE_EVERY_REQUEST = True

CORS_ORIGIN_WHITELIST = (
    INKSHOP_BASE_URL,
    'localhost',
)
CORS_ORIGIN_ALLOW_ALL = True


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': POSTGRES_DB,
        'USER': POSTGRES_USER,
        'PASSWORD': POSTGRES_PASSWORD,
        'HOST': 'db',
        'PORT': 5432,
    }
}
if 'CIRCLECI' in os.environ:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'circle_test',
        'USER': 'ubuntu',
    }
TEST_MODE = False
DISABLE_ENCRYPTION_FOR_TESTS = False
if 'test' in sys.argv:
    TEST_MODE = True
    logging.disable(logging.CRITICAL)
    CELERY_ALWAYS_EAGER = True
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True
    CACHES['default']['PREFIX'] = 'test'
    EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

    if "DISABLE_ENCRYPTION_FOR_TESTS" in os.environ and os.environ["DISABLE_ENCRYPTION_FOR_TESTS"] == "True":
        DISABLE_ENCRYPTION_FOR_TESTS = True


# Static
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
STATIC_ROOT = join(PROJECT_DIR, "collected_static")
STATIC_URL = '/static/'
COMPRESS_ROOT = STATIC_ROOT

COMPRESS_PRECOMPILERS = (
    ('text/less', 'lessc {infile} {outfile}'),
)

COMPRESS_CSS_FILTERS = (
    'compressor.filters.cssmin.CSSCompressorFilter',
)

COMPRESS_JS_FILTERS = (
    # 'compressor.filters.jsmin.SlimItFilter',
)
COMPRESS_ENABLED = True
HTML_MINIFY = True

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Background Workers
# CELERY_BROKER_URL = 'amqp://rabbitmq:rabbitmq@rabbitmq:5672'
# BROKER_URL = 'amqp://rabbitmq:rabbitmq@rabbitmq:5672'

CELERY_BROKER_URL = 'redis://redis:6379/0'
BROKER_URL = 'redis://redis:6379/0'

CELERYBEAT_SCHEDULE = {}
CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']
CELERYD_TASK_TIME_LIMIT = 15
CELERY_ROUTES = {}
CELERY_TASK_ROUTES = CELERY_ROUTES
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ALWAYS_EAGER = False


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_URL = '/static/'
