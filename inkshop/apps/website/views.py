from django.conf import settings
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt

from annoying.decorators import render_to, ajax_request


@render_to("website/home.html")
def home(request):
    return locals()


def page_or_post(request, page_slug):
    return locals()
