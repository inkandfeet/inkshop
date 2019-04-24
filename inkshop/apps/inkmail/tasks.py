import datetime
import json
import logging
import requests

from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail as django_send_mail
from celery.task import task, periodic_task
from django.utils import timezone
from inkmail.helpers import queue_transactional_message
from inkmail.models import Subscription, OutgoingMessage


@periodic_task(run_every=datetime.timedelta(seconds=5), expires=10)
def hello():
    message = "Hi at %s" % timezone.now()
    print(message)
    pass


@task
def send_subscription_confirmation(subscription_pk):
    print("send_subscription_confirmation")
    s = Subscription.objects.select_related('person').get(pk=subscription_pk)
    if (
        not s.double_opted_in
        and not s.unsubscribed
        and not s.person.banned
        and not s.person.hard_bounced
    ):
        queue_transactional_message(s.newsletter.confirm_message, s.person)


@periodic_task(run_every=datetime.timedelta(seconds=30), expires=30)
def process_outgoing_message_queue():
    # Queue brand new messages
    # print("process_outgoing_message_queue")
    window_starts_at = timezone.now()
    # - datetime.timedelta(seconds=30)
    for om in OutgoingMessage.objects.filter(send_at__lte=window_starts_at, attempt_started=False):
        # print("om")
        # print(om)
        send_outgoing_message.delay(om.pk)

    # TODO: Queue retries


@task
def send_outgoing_message(om_pk):
    # print("send_outgoing_message")
    om = OutgoingMessage.objects.get(pk=om_pk)
    om.send()
