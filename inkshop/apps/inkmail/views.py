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
from ipware import get_client_ip

from inkmail.models import Newsletter, Subscription
from inkmail.tasks import send_subscription_confirmation
from people.models import Person
from utils.encryption import normalize_lower_and_encrypt, normalize_and_encrypt


@render_to("inkmail/home.html")
def home(request):
    return locals()


@csrf_exempt
@render_to("inkmail/subscribe.html")
def subscribe(request):
    s = None
    if request.is_ajax():
        ajax_response = {
            "success": False
        }
        if request.method == "POST":
            data = json.loads(request.body)
            if "email" in data and "newsletter" in data and "subscription_url" in data:
                encrypted_email = normalize_lower_and_encrypt(data['email'])
                if Newsletter.objects.filter(internal_name=data["newsletter"]).count():
                    n = Newsletter.objects.get(internal_name=data["newsletter"])
                    encrypted_first_name = None
                    if "first_name" in data:
                        encrypted_first_name = normalize_and_encrypt(data["first_name"])
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
                    if created:
                        s.subscription_url = data["subscription_url"]
                        s.subscribed_from_ip, _ = get_client_ip(request)
                        s.save()
                    ajax_response["success"] = True

    else:
        if request.method == "POST":
            if "email" in request.POST and "newsletter" in request.POST and "subscription_url" in request.POST:
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
                        subscription_url=request.POST["subscription_url"],
                    )
                    if created:
                        s.subscription_url = request.POST["subscription_url"]
                        s.subscribed_from_ip, _ = get_client_ip(request)
                        s.save()
    if not s:
        # Did not create subscription
        if request.is_ajax():
            return HttpResponse(json.dumps(ajax_response), content_type="application/json", status=422)
        else:
            return HttpResponse(status=422)
    else:
        send_subscription_confirmation.delay(s.pk)

    if request.is_ajax():
        return HttpResponse(json.dumps(ajax_response), content_type="application/json", status=200)
    else:
        return locals()


@render_to("inkmail/email_confirmation.html")
def confirm_subscription(request, opt_in_key):
    s = Subscription.objects.get(opt_in_key=opt_in_key)
    s.double_opted_in = True
    s.double_opted_in_at = timezone.now()
    s.save()

    p = s.person
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
