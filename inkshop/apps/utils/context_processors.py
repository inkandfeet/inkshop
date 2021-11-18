from django.conf import settings
from ipware import get_client_ip


def is_debug(context):
    if "ngrok" in settings.INKSHOP_DOMAIN:
        dots_url = "https://%s/dots/event/" % settings.INKSHOP_DOMAIN

    return {
        'IS_DEBUG': settings.DEBUG,
        'GOOGLE_ANALYTICS_ID': settings.GOOGLE_ANALYTICS_ID,
        'GOOGLE_ADS_ID': settings.GOOGLE_ADS_ID,
        'INKSHOP_DOMAIN': settings.INKSHOP_DOMAIN,
        'ROLLBAR_TOKEN': settings.ROLLBAR_TOKEN,
        'DOTS_URL': dots_url,
        'PAGE_URL': context.build_absolute_uri(context.get_full_path()).replace("http://", "https://"),
        'PAGE_DOMAIN': context.build_absolute_uri("/")[:-1].replace("http://", "https://"),
        'IS_FACEBOOK_BOT': "::face:b00c" in get_client_ip(context) or "fbclid" in context.GET
    }
