from django.conf import settings


def is_debug(context):
    return {
        'IS_DEBUG': settings.DEBUG
    }
