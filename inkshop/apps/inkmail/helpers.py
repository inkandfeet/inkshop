import datetime
import json
import logging
import requests

from django.conf import settings
from django.template.loader import render_to_string
from celery.task import task, periodic_task
from django.utils import timezone


def send_message(*args, **kwargs):
    """Very light wrapper around queue_message in case we want to expose an immediate=True flag in the future."""
    queue_message(*args, **kwargs)


def send_newsletter_message(*args, **kwargs):
    """Very light wrapper around queue_newsletter_message in case we want to expose an immediate=True flag in the future."""
    queue_newsletter_message(*args, **kwargs)


def send_transactional_message(message=None, person=None):
    """ery light wrapper around queue_message in case we want to expose an immediate=True flag in the future."""
    queue_transactional_message(message, person)


def queue_message(message, subscription, at=None, scheduled_newsletter_message=None):
    """Sends a message to a particular subscriber"""
    from inkmail.models import OutgoingMessage  # Avoid circular imports
    if not at:
        at = timezone.now()

    OutgoingMessage.objects.create(
        subscription=subscription,
        person=subscription.person,
        message=message,
        send_at=at,
    )


def queue_newsletter_message(scheduled_newsletter_message, at=None):
    """Sends a message to a particular subscriber"""
    from inkmail.models import OutgoingMessage  # Avoid circular imports

    if not at:
        at = timezone.now()

    for subscription in scheduled_newsletter_message.recipients:
        OutgoingMessage.objects.create(
            scheduled_newsletter_message=scheduled_newsletter_message,
            person=subscription.person,
            subscription=subscription,
            message=scheduled_newsletter_message.message,
            send_at=at,
        )


def queue_transactional_message(message, person, at=None, scheduled_newsletter_message=None):
    """Sends a message to a particular subscriber"""
    from inkmail.models import OutgoingMessage  # Avoid circular imports

    if not at:
        at = timezone.now()

    OutgoingMessage.objects.create(
        person=person,
        message=message,
        scheduled_newsletter_message=scheduled_newsletter_message,
        send_at=at,
    )
