import datetime
import json
import logging
import requests

from django.conf import settings
from django.template.loader import render_to_string
from celery.task import task, periodic_task
from django.utils import timezone



def queue_message(message, subscription, at=None, scheduled_newsletter_message=None):
    """Sends a message to a particular subscriber"""
    from inkmail.models import Subscription, Message, OutgoingMessage  # Avoid circular imports

    if not at:
        at = timezone.now()

    s = Subscription.objects.select_related('person').get(pk=subscription_pk)
    message = Message.objects.get(pk=message_id)

    OutgoingMessage.objects.create(
        person=s.person,
        message=message,
        scheduled_newsletter_message=scheduled_newsletter_message,
        send_at=at,
        transactional=False,
    )


def queue_transactional_message(message, subscription, at=None, scheduled_newsletter_message=None):
    """Sends a message to a particular subscriber"""
    from inkmail.models import Subscription, Message, OutgoingMessage  # Avoid circular imports

    if not at:
        at = timezone.now()

    s = Subscription.objects.select_related('person').get(pk=subscription_pk)
    message = Message.objects.get(pk=message_id)

    OutgoingMessage.objects.create(
        person=s.person,
        subscription=s,
        message=message,
        scheduled_newsletter_message=scheduled_newsletter_message,
        send_at=at,
        transactional=True,
    )

    # send_mail.delay(subscription_pk, subject, body)


@task
def send_opt_in_message(message_id, subscription_pk):
    """Sends a message to a particular subscriber"""
    from inkmail.models import Subscription, Message  # Avoid circular imports

    s = Subscription.objects.select_related('person').get(pk=subscription_pk)
    message = Message.objects.get(pk=message_id)

    subject, body = message.render_subject_and_body(subscription=s)

    send_transactional_email(subscription_pk, subject, body)


@task
def send_transactional_message(message_id, subscription_pk):
    """Sends a message to a particular person, even if they're not a subscriber"""
    from inkmail.models import Subscription, Message  # Avoid circular imports

    s = Subscription.objects.select_related('person').get(pk=subscription_pk)
    message = Message.objects.get(pk=message_id)

    subject, body = message.render_subject_and_body(subscription=s)

    send_transactional_email(subscription_pk, subject, body)
