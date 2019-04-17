import datetime
import json
import logging
import requests

from django.conf import settings
from django.core.mail import send_mail as django_send_mail
from django.template.loader import render_to_string
from celery.task import task, periodic_task
from django.utils import timezone


@periodic_task(run_every=datetime.timedelta(seconds=5), expires=10)
def hello():
    message = "Hi at %s" % timezone.now()
    print(message)


@task
def send_mail(subscriber_pk, subject, body):
    # Avoid circular imports
    from inkmail.models import Subscription
    s = Subscription.objects.get(pk=subscriber_pk)

    if s.double_opted_in and not s.unsubscribed:
        # Safe to send email.
        django_send_mail(subject, body, s.newsletter.full_from_email, [s.person.email, ], fail_silently=False)


@task
def send_even_if_not_double_opted_in(subscriber_pk, subject, body):
    # Avoid circular imports
    from inkmail.models import Subscription
    s = Subscription.objects.get(pk=subscriber_pk)

    if not s.unsubscribed:
        # Safe to send email.
        pass


@task
def send_transactional_email(subscriber_pk, subject, body):
    # Avoid circular imports
    from inkmail.models import Subscription
    s = Subscription.objects.get(pk=subscriber_pk)

    if not s.unsubscribed:
        # Safe to send email.
        pass
