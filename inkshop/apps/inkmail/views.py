import datetime
import json
import logging
import time

from django.db import IntegrityError
from django.conf import settings
from django.core.mail import mail_admins
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from annoying.decorators import render_to, ajax_request

from inkmail.models import Newsletter, Subscription
from people.models import Person
from utils.encryption import normalize_lower_and_encrypt, normalize_and_encrypt


@render_to("inkmail/home.html")
def home(request):
    return locals()


@render_to("inkmail/subscribe.html")
def subscribe(request):
    s = None
    if request.method == "POST":
        if "email" in request.POST and "newsletter" in request.POST:
            encrypted_email = normalize_lower_and_encrypt(request.POST['email'])
            if Newsletter.objects.filter(internal_name=request.POST["newsletter"]).count():
                n = Newsletter.objects.get(internal_name=request.POST["newsletter"])
                encrypted_first_name = None
                if "first_name" in request.POST:
                    encrypted_first_name = normalize_and_encrypt(request.POST["first_name"])
                if Person.objects.filter(encrypted_email=encrypted_email):
                    p = Person.objects.get(encrypted_email=encrypted_email)
                else:
                    p = Person.objects.create(
                        encrypted_email=encrypted_email,
                        encrypted_first_name=encrypted_first_name,
                    )

                s, created = Subscription.objects.get_or_create(
                    person=p,
                    newsletter=n,
                )
    if s:
        # for JSON response
        pass
    else:
        return HttpResponse(status=422)

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
