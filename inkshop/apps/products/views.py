from base64 import b64decode
import datetime
import json
import logging
import time

from django.conf import settings
from django.core.mail import mail_admins
from django.contrib.auth import authenticate, login
from django.db import IntegrityError
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from annoying.decorators import render_to, ajax_request
from utils.factory import Factory
from inkmail.models import Organization
from product.models import Product


@render_to("products/home.html")
def home(request):
    o = Organization.get()
    return locals()
