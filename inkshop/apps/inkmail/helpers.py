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
    from inkmail.models import OutgoingMessage  # Avoid circular imports
    if not at:
        at = timezone.now()

    OutgoingMessage.objects.create(
        subscription=subscription,
        person=subscription.person,
        message=message,
        send_at=at,
    )


@task
def queue_newsletter_message(scheduled_newsletter_message_hashid, at=None):
    """Sends a message to a particular subscriber"""
    from inkmail.models import OutgoingMessage, ScheduledNewsletterMessage  # Avoid circular imports
    scheduled_newsletter_message = ScheduledNewsletterMessage.objects.get(hashid=scheduled_newsletter_message_hashid)

    if (
        scheduled_newsletter_message
        and scheduled_newsletter_message.enabled
        and not scheduled_newsletter_message.complete
    ):
        if not at:
            if scheduled_newsletter_message.send_at_date:
                # TODO: Use local time
                # scheduled_newsletter_message.use_local_time
                at = scheduled_newsletter_message.send_at_date
                time = datetime.time()
                at = datetime.datetime.combine(at, time)
                if scheduled_newsletter_message.send_at_hour:
                    at = at.replace(
                        hour=scheduled_newsletter_message.send_at_hour,
                    )
                if scheduled_newsletter_message.send_at_minute:
                    at = at.replace(
                        minute=scheduled_newsletter_message.send_at_minute,
                    )
                at = at.replace(
                    tzinfo=timezone.now().tzinfo
                )
            else:
                at = timezone.now()

        for subscription in scheduled_newsletter_message.recipients:
            OutgoingMessage.objects.create(
                scheduled_newsletter_message=scheduled_newsletter_message,
                person=subscription.person,
                subscription=subscription,
                message=scheduled_newsletter_message.message,
                send_at=at,
            )
        scheduled_newsletter_message.complete = True
        scheduled_newsletter_message.save()
    else:
        logging.warn("Message not enabled or has already been sent.")


def queue_transactional_message(message, person, at=None, scheduled_newsletter_message=None, subscription=None):
    """Sends a message to a particular subscriber"""
    from inkmail.models import OutgoingMessage  # Avoid circular imports

    if not at:
        at = timezone.now()

    if not message.transactional:
        raise Exception("Attempting to queue a non-transactional message in the transactional queue.")

    OutgoingMessage.objects.create(
        person=person,
        message=message,
        scheduled_newsletter_message=scheduled_newsletter_message,
        subscription=subscription,
        send_at=at
    )
