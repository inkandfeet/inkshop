import datetime
import json
import logging
import requests

from django.conf import settings
from django.template.loader import render_to_string
from celery.task import task, periodic_task
from django.utils import timezone
from inkmail.helpers import send_message, send_transactional_message
from inkmail.models import Subscription


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
