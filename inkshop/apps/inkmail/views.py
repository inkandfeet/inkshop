import datetime
import json
import logging
import time

from django.db import IntegrityError
from django.conf import settings
from django.core.mail import mail_admins
from django.contrib.auth import authenticate, login
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from binascii import hexlify, unhexlify
from simplecrypt import encrypt, decrypt

from annoying.decorators import render_to, ajax_request

from people.models import Person


@render_to("inkmail/home.html")
def home(request):
    return locals()


@render_to("inkmail/email_confirmation.html")
def confirm_email(request, email_key):
    p = Person.objects.get(email_confirm_key=email_key)
    p.email_verified = True
    p.save()
    email_confirmed = True
    return locals()


@render_to("inkmail/opt_out.html")
def opt_out(request, reader_opt_out_key):
    p = Person.objects.get(opt_out_key=reader_opt_out_key)
    p.opted_out_of_email = True
    p.save()
    return locals()
