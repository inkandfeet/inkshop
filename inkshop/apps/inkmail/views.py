import datetime
import json
import logging
import time

from django.db import IntegrityError
from django.conf import settings
from django.core.mail import mail_admins
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from utils.helpers import reverse
from django.views.decorators.csrf import csrf_exempt

from annoying.decorators import render_to, ajax_request
from ipware import get_client_ip

from archives.models import HistoricalEvent
from inkmail.models import Newsletter, Subscription, OutgoingMessage, Organization
from inkmail.tasks import send_subscription_confirmation, send_subscription_welcome
from people.models import Person
from utils.encryption import normalize_lower_and_encrypt, normalize_and_encrypt, lookup_hash, f


@render_to("inkmail/home.html")
def home(request):
    o = Organization.get()
    return locals()


@csrf_exempt
@render_to("inkmail/subscribe.html")
def subscribe(request):
    o = Organization.get()
    s = None
    if request.is_ajax():
        ajax_response = {
            "success": False
        }
        if request.method == "POST":
            data = json.loads(request.body)
            if "email" in data and "newsletter" in data and "subscription_url" in data:
                hashed_email = lookup_hash(data['email'])
                if Newsletter.objects.filter(internal_name=data["newsletter"]).count():
                    n = Newsletter.objects.get(internal_name=data["newsletter"])
                    if Person.objects.filter(hashed_email=hashed_email).count() > 0:
                        p = Person.objects.get(hashed_email=hashed_email)
                        if "first_name" in data:
                            p.first_name = data["first_name"]
                    else:
                        p = Person.objects.create(
                            hashed_email=hashed_email,
                        )
                        p.email = data["email"]
                        if "first_name" in data:
                            p.first_name = data["first_name"]
                    p.save()

                    s, created = Subscription.objects.get_or_create(
                        person=p,
                        newsletter=n,
                    )
                    if created or s.unsubscribed:
                        s.subscribed_at = timezone.now()
                        s.unsubscribed = False
                        s.unsubscribed_at = None
                        s.subscription_url = data["subscription_url"]
                        s.subscribed_from_ip, _ = get_client_ip(request)
                        s.save()
                    ajax_response["success"] = True

    else:
        if request.method == "POST":
            if "email" in request.POST and "newsletter" in request.POST and "subscription_url" in request.POST:
                hashed_email = lookup_hash(request.POST['email'])
                if Newsletter.objects.filter(internal_name=request.POST["newsletter"]).count():
                    n = Newsletter.objects.get(internal_name=request.POST["newsletter"])

                    if Person.objects.filter(hashed_email=hashed_email).count() > 0:
                        p = Person.objects.get(hashed_email=hashed_email)
                        if "first_name" in request.POST:
                            p.first_name = request.POST["first_name"]
                    else:
                        p = Person.objects.create(
                            hashed_email=hashed_email,
                        )
                        p.email = request.POST["email"]
                        if "first_name" in request.POST:
                            p.first_name = request.POST["first_name"]
                    p.save()

                    s, created = Subscription.objects.get_or_create(
                        person=p,
                        newsletter=n,
                    )
                    if created or s.unsubscribed:
                        s.subscribed_at = timezone.now()
                        s.unsubscribed = False
                        s.unsubscribed_at = None

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
        s.opt_in_link
        HistoricalEvent.log(person=p, event_type="subscribed", newsletter=n, subscription=s)
        if s.double_opted_in is False:
            send_subscription_confirmation.delay(s.pk)
        else:
            if request.is_ajax():
                ajax_response["message"] = "Resubscribed.  You're all set!"
            else:
                message = "Resubscribed.  You're all set!"
                resubscribed = True

    if request.is_ajax():
        return HttpResponse(json.dumps(ajax_response), content_type="application/json", status=200)
    else:
        return locals()


@render_to("inkmail/email_confirmation.html")
def confirm_subscription(request, opt_in_key):
    o = Organization.get()
    s = Subscription.objects.get(opt_in_key=opt_in_key)
    already_double_opted_in = True
    if not s.double_opted_in:
        already_double_opted_in = False
        s.double_opted_in = True
        s.double_opted_in_at = timezone.now()
        s.save()

    p = s.person
    p.email_verified = True
    p.save()
    email_confirmed = True

    if not already_double_opted_in:
        send_subscription_welcome.delay(s.pk)

    s = Subscription.objects.get(pk=s.pk)
    HistoricalEvent.log(
        person=p,
        event_type="double-opt-in",
        subscription=s,
        newsletter=s.newsletter,
    )

    return locals()


@render_to("inkmail/email_confirmation.html")
def transfer_subscription(request, transfer_code):
    o = Organization.get()
    # This is a special link for users to opt-in from an existing newsletter.
    s = None
    if "e" in request.GET:
        hashed_email = lookup_hash(request.GET["e"].replace(" ", "+"))
        if Newsletter.objects.filter(hashid=transfer_code).count():
            n = Newsletter.objects.get(hashid=transfer_code)

            if Person.objects.filter(hashed_email=hashed_email).count() > 0:
                p = Person.objects.get(hashed_email=hashed_email)
                if "f" in request.GET:
                    p.first_name = request.GET["f"]
            else:
                p = Person.objects.create(
                    hashed_email=hashed_email,
                )
                p.email = request.GET["e"].replace(" ", "+")
                if "f" in request.GET:
                    p.first_name = request.GET["f"]
            p.save()

            s, created = Subscription.objects.get_or_create(
                person=p,
                newsletter=n,
            )
            if created or s.unsubscribed:
                s.subscribed_at = timezone.now()
                s.unsubscribed = False
                s.unsubscribed_at = None

                s.subscription_url = "transfer-subscription"
                s.subscribed_from_ip, _ = get_client_ip(request)
                s.save()

            already_double_opted_in = True
            if not s.double_opted_in:
                already_double_opted_in = False
                s.double_opted_in = True
                s.double_opted_in_at = timezone.now()
                s.save()

            p = s.person
            p.email_verified = True
            p.save()
            email_confirmed = True

        if not already_double_opted_in:
            send_subscription_welcome.delay(s.pk)

    if s is not None:
        s = Subscription.objects.get(pk=s.pk)
        HistoricalEvent.log(
            person=p,
            event_type="transfer-subscription",
            subscription=s,
            newsletter=s.newsletter,
        )
    else:
        return HttpResponse(status=422)

    return locals()


@render_to("inkmail/resubscribed.html")
def resubscribe(request, resubscribe_key):
    o = Organization.get()
    om = OutgoingMessage.objects.get(unsubscribe_hash=resubscribe_key)
    if om.subscription:
        om.subscription.resubscribe()
        HistoricalEvent.log(
            person=om.person,
            event_type="resubscribe",
            subscription=om.subscription,
            outgoingmessage=om,
        )
    return locals()


@render_to("inkmail/unsubscribed.html")
def unsubscribe(request, unsubscribe_key):
    o = Organization.get()
    om = OutgoingMessage.objects.get(unsubscribe_hash=unsubscribe_key)
    if om.subscription:
        om.subscription.unsubscribe()
        HistoricalEvent.log(
            person=om.person,
            event_type="unsubscribe",
            subscription=om.subscription,
            outgoingmessage=om,
        )

    return locals()


@render_to("inkmail/delete_account_start.html")
def delete_account(request, delete_key):
    o = Organization.get()
    try:
        om = OutgoingMessage.objects.get(delete_hash=delete_key)
        person = om.person

        if request.POST.get("submit") == "yes":
            # if om.subscription:
            #     om.subscription.unsubscribe()
            HistoricalEvent.log(
                person=om.person,
                event_type="delete_account",
                subscription=om.subscription,
                outgoingmessage=om,
            )
            om.person.delete()
            return redirect(reverse('inkmail:delete_account_done'))

        return locals()
    except:
        return redirect(reverse('inkmail:delete_account_done'))


@render_to("inkmail/delete_account_complete.html")
def delete_account_done(request):
    o = Organization.get()
    return locals()


@render_to("inkmail/loved.html")
def love_message(request, love_hash):
    o = Organization.get()
    om = OutgoingMessage.objects.get(love_hash=love_hash)
    om.loved = True
    om.loved_at = timezone.now()
    om.save()
    HistoricalEvent.log(
        person=om.person,
        event_type="loved_message",
        subscription=om.subscription,
        outgoingmessage=om,
    )
    # if om.subscription:
    #     om.subscription.unsubscribe()

    return locals()
