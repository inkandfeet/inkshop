import datetime
import json
import logging
import requests

from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail as django_send_mail
from celery.task import task, periodic_task
from django.utils import timezone
from inkmail.helpers import queue_transactional_message, queue_message
from inkmail.models import Subscription, OutgoingMessage, Person, Message


@periodic_task(run_every=datetime.timedelta(seconds=120), expires=10)
def hello():
    message = "Hi at %s" % timezone.now()
    print(message)
    pass


@task
def send_subscription_confirmation(subscription_pk):
    s = Subscription.objects.select_related('person').get(pk=subscription_pk)
    if (
        not s.double_opted_in
        and not s.unsubscribed
        and not s.person.banned
        and not s.person.hard_bounced
    ):
        queue_transactional_message(s.newsletter.confirm_message, s.person, subscription=s)


@task
def send_subscription_welcome(subscription_pk):
    s = Subscription.objects.select_related('person').get(pk=subscription_pk)
    if (
        not s.unsubscribed
        and not s.person.banned
        and not s.person.hard_bounced
    ):
        queue_message(s.newsletter.welcome_message, s)


@periodic_task(run_every=datetime.timedelta(seconds=30), expires=30)
def process_outgoing_message_queue():
    # Queue brand new messages
    window_starts_at = timezone.now()
    # - datetime.timedelta(seconds=30)
    for om in OutgoingMessage.objects.filter(send_at__lte=window_starts_at, attempt_started=False):
        if settings.TEST_MODE:
            send_outgoing_message.delay(om.pk)
        else:
            send_outgoing_message.delay(om.pk)

    # TODO: Queue retries


@task
def send_outgoing_message(om_pk):
    om = OutgoingMessage.objects.get(pk=om_pk)
    om.send()


@periodic_task(run_every=datetime.timedelta(minutes=5), expires=1200)
def check_for_unsubscribes():
    if hasattr(settings, "IS_LIVE") and settings.IS_LIVE:
        base_mailgun_url = "https://api.mailgun.net/v3/%s/" % (
            settings.MAILGUN_SENDER_DOMAIN,
        )
        events_api_url = "%sevents" % base_mailgun_url

        # event_query_data = {
        #     "event": "unsubscribed",
        # }
        # r = requests.get(events_api_url, auth=("api", settings.MAILGUN_API_KEY), params=event_query_data)
        # data = json.loads(r.content)

        # print("Unsubscribes")
        # for e in data["items"]:
        #     print(e)

        # event_query_data = {"event": "rejected", }
        # r = requests.get(events_api_url, auth=("api", settings.MAILGUN_API_KEY), params=event_query_data)
        # data = json.loads(r.content)
        # print("rejected")
        # for e in data["items"]:
        #     print(e)

        event_query_data = {"event": "complained", }
        r = requests.get(events_api_url, auth=("api", settings.MAILGUN_API_KEY), params=event_query_data)
        data = json.loads(r.content)
        # print("complained")
        for e in data["items"]:
            try:
                email = e["recipient"]
                p = Person.get_by_email(email)
                # reason = e["delivery-status"]["message"]
                reason = "complained"
                try:
                    bouncing_message = Message.objects.get(subject=e["messsage"]["subject"])
                except:
                    bouncing_message = None
                # print("hard bounce: %s %s %s for %s" % (
                #     email,
                #     reason,
                #     bouncing_message,
                #     p,
                # ))
                p.hard_bounce(reason=reason, bouncing_message=bouncing_message, raw_mailgun_data=e)
            except:
                # print(e)
                import traceback
                traceback.print_exc()
                pass

        event_query_data = {"event": "failed", }
        r = requests.get(events_api_url, auth=("api", settings.MAILGUN_API_KEY), params=event_query_data)
        data = json.loads(r.content)
        # print("failed")
        for e in data["items"]:
            try:
                if "severity" in e and e["severity"] == "permanent":
                    email = e["recipient"]
                    p = Person.get_by_email(email)
                    reason = e["delivery-status"]["message"]
                    try:
                        bouncing_message = Message.objects.get(subject=e["messsage"]["subject"])
                    except:
                        bouncing_message = None
                    if not reason:
                        reason = e["delivery-status"]["description"]
                    # print("permanent fail: %s %s %s for %s" % (
                    #     email,
                    #     reason,
                    #     bouncing_message,
                    #     p,
                    # ))
                    p.hard_bounce(reason=reason, bouncing_message=bouncing_message, raw_mailgun_data=e)
                else:
                    # print("%s - temporary" % email)
                    pass
            except:
                # print(e)
                import traceback
                traceback.print_exc()
                pass
