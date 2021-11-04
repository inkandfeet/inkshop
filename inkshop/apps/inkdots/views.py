from base64 import b64decode
import datetime
import json
import logging
import time
import traceback

from django.conf import settings
from django.core.mail import mail_admins
from django.contrib.auth import authenticate, login
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from ipware import get_client_ip

from annoying.decorators import render_to, ajax_request
from inkmail.models import Organization
from inkdots.models import Event

from django.db import IntegrityError


@render_to("inkdots/home.html")
def home(request):
    o = Organization.get()
    return locals()


@csrf_exempt
@ajax_request
def event(request):
    try:
        e = json.loads(request.body)

        qs = ""
        if "?" in e["url"]:
            qs = e["url"].split("?")[1]
        Event.objects.create(
            event_type=e["event_type"],
            base_url=e["url"].split("//")[1].split("?")[0],
            querystring=qs,
            full_url=e["url"],
            data=json.dumps(e["data"]),
            request_ip=get_client_ip(request)[0],
            request_ua=request.META.get("HTTP_USER_AGENT", "None"),
        )
        return {"success": True}
    except:
        traceback.print_exc()
        return {"success": False}
