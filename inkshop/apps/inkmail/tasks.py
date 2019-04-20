import datetime
import json
import logging
import requests

from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail as django_send_mail
from celery.task import task, periodic_task
from django.utils import timezone
from inkmail.helpers import send_message, send_transactional_message
from inkmail.models import Subscription, OutgoingMessage


@periodic_task(run_every=datetime.timedelta(seconds=5), expires=10)
def hello():
    message = "Hi at %s" % timezone.now()
    print(message)


@task
def send_subscription_confirmation(subscription_pk):
    s = Subscription.objects.select_related('person').get(pk=subscription_pk)
    if (
        not s.double_opted_in
        and not s.unsubscribed
        and not s.person.banned
        and not s.person.hard_bounced
    ):
        send_transactional_message(s.newsletter.confirm_message.pk, subscription_pk)


@periodic_task(run_every=datetime.timedelta(seconds=30), expires=30)
def queue_next_messages():
    # Queue brand new messages
    window_starts_at = timezone.now() - datetime.timedelta(seconds=30)
    for om in OutgoingMessage.objects.filter(send_at__lte=window_starts_at, attempt_started=False):
        om.send()

    # TODO: Queue retries


@task
def send_mail(subscription_pk, subject, body):
    from inkmail.models import Subscription  # Avoid circular imports
    sent_successfully = False
    try:
        s = Subscription.objects.select_related('person').get(pk=subscription_pk)

        if (
            s.double_opted_in
            and not s.unsubscribed
            and not s.person.banned
            and not s.person.hard_bounced
        ):
            # Safe to send email.
            django_send_mail(subject, body, s.newsletter.full_from_email, [s.person.email, ], fail_silently=False)
            sent_successfully = True
    except:
        pass

    # Log attempt.
    if sent_successfully:
        pass


@task
def send_transactional_email(subscription_pk, subject, body):
    # Avoid circular imports
    from inkmail.models import Subscription
    s = Subscription.objects.select_related('person').get(pk=subscription_pk)

    if (
        # not s.unsubscribed and  # TODO: Decide on this.
        not s.person.banned
        and not s.person.hard_bounced
    ):
        # Safe to send email.
        django_send_mail(subject, body, s.newsletter.full_from_email, [s.person.email, ], fail_silently=False)
