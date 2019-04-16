from base64 import b64decode
import datetime
import json
import logging
import time

from django.conf import settings
from django.core.mail import mail_admins
from django.contrib.auth import authenticate, login
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from annoying.decorators import render_to, ajax_request

from django.db import IntegrityError


@render_to("inkdots/home.html")
def home(request):
    return locals()
