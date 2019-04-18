import datetime
import json
import logging
import requests

from django.conf import settings
from django.core.mail import send_mail as django_send_mail
from django.template.loader import render_to_string
from celery.task import task, periodic_task
from django.utils import timezone


@task
def send_message(message_id, subscription_pk):
    """Sends a message to a particular subscriber"""
    from inkmail.models import Subscription, Message  # Avoid circular imports

    s = Subscription.objects.select_related('person').get(pk=subscription_pk)
    message = Message.objects.get(pk=message_id)

    subject, body = message.render_subject_and_body(subscription=s)

    send_mail.delay(subscription_pk, subject, body)


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


@task
def send_mail(subscription_pk, subject, body):
    from inkmail.models import Subscription  # Avoid circular imports

    s = Subscription.objects.select_related('person').get(pk=subscription_pk)

    if (
        s.double_opted_in and
        not s.unsubscribed and
        not s.person.banned and
        not s.person.hard_bounced
    ):
        # Safe to send email.
        django_send_mail(subject, body, s.newsletter.full_from_email, [s.person.email, ], fail_silently=False)


@task
def send_even_if_not_double_opted_in(subscription_pk, subject, body):
    # Avoid circular imports
    from inkmail.models import Subscription
    s = Subscription.objects.select_related('person').get(pk=subscription_pk)

    if (
        not s.unsubscribed and
        not s.person.banned and
        not s.person.hard_bounced
    ):
        # Safe to send email.
        django_send_mail(subject, body, s.newsletter.full_from_email, [s.person.email, ], fail_silently=False)


@task
def send_transactional_email(subscription_pk, subject, body):
    # Avoid circular imports
    from inkmail.models import Subscription
    s = Subscription.objects.select_related('person').get(pk=subscription_pk)

    if (
        not s.unsubscribed and  # TODO: Decide on this.
        not s.person.banned and
        not s.person.hard_bounced
    ):
        # Safe to send email.
        django_send_mail(subject, body, s.newsletter.full_from_email, [s.person.email, ], fail_silently=False)
