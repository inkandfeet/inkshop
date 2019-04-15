import datetime
import hashlib
import logging
import random
import time
import uuid
from base64 import b64encode
from io import BytesIO
from PIL import Image, ImageOps
from tempfile import NamedTemporaryFile

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.signals import user_logged_in
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils import timezone

from people.models import Person
from utils.models import BaseModel


class Message(BaseModel):
    subject = models.CharField(max_length=254, blank=True, null=True)
    body_text_unrendered = models.TextField(blank=True, null=True)
    body_html_unrendered = models.TextField(blank=True, null=True)


class MailingList(BaseModel):
    name = models.CharField(max_length=254, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    confirm_message = models.ForeignKey(
        Message,
        on_delete=models.SET_NULL, blank=True, null=True, related_name="list_for_confirm"
    )
    welcome_message = models.ForeignKey(
        Message,
        on_delete=models.SET_NULL, blank=True, null=True, related_name="list_for_welcome"
    )

    unsubscribe_if_no_hearts_after_days = models.BooleanField(default=False)
    unsubscribe_if_no_hearts_after_days_num = models.IntegerField(blank=True, null=True, default=184)
    unsubscribe_if_no_hearts_after_messages = models.BooleanField(default=True)
    unsubscribe_if_no_hearts_after_messages_num = models.IntegerField(blank=True, null=True, default=26)


class Subscription(BaseModel):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    mailing_list = models.ForeignKey(MailingList, on_delete=models.CASCADE)
    subscribed_at = models.DateTimeField(blank=True, null=True, default=timezone.now)
    subscribed_from_url = models.TextField(blank=True, null=True)
    double_opted_in_at = models.DateTimeField(blank=True, null=True, default=timezone.now)
    has_set_never_unsubscribe = models.BooleanField(default=False)
    unsubscribed_at = models.DateTimeField(blank=True, null=True)

    last_action = models.DateTimeField(blank=True, null=True, default=timezone.now)


class ScheduledMessage(BaseModel):
    message = models.ForeignKey(Message, blank=True, null=True, on_delete=models.SET_NULL)
    mailing_list = models.ForeignKey(MailingList, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=False)
    complete = models.BooleanField(default=False)

    send_at_date = models.DateField(blank=True, null=True, default=timezone.now)
    send_at_hour = models.IntegerField()
    send_at_minute = models.IntegerField()
    use_local_time = models.BooleanField(default=True)  # if False, use UTC.

    num_scheduled = models.IntegerField(default=0)
    # num_queued = models.IntegerField(default=0) ?
    num_sent = models.IntegerField(default=0)

    def recipients(self):
        return self.mailing_list.subscribers


class OutgoingMessage(BaseModel):
    scheduled_message = models.ForeignKey(ScheduledMessage, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    send_at = models.DateTimeField()
    attempt_complete = models.BooleanField(default=False)


class OutgoingMessageAttemptTombstone(BaseModel):
    send_time = models.DateTimeField()
    outgoing_message = models.ForeignKey(OutgoingMessage, on_delete=models.SET_NULL, blank=True, null=True)
    encrypted_email = models.TextField(blank=True, null=True)
    encrypted_message_subject = models.TextField(blank=True, null=True)
    encrypted_message_body = models.TextField(blank=True, null=True)
    send_success = models.NullBooleanField()
    send_error = models.TextField(blank=True, null=True)


# class Sequence(BaseModel):
#     name = models.CharField(max_length=254, blank=True, null=True)

# class SequenceStep(BaseModel):
#     sequence = models.ForeignKey(SequenceStep, on_delete=models.CASCADE)

#     previous_step = models.ForeignKey(Sequence, blank=True, null=True)
#     wait_time_s = models.IntegerField(blank=True, null=True)

#     step_number = models.IntegerField()

#     send_at = models.DateTimeField()
#     ignore_if_added_after = models.BooleanField()

#     send_message = models.ForeignKey(Message, blank=True, null=True, on_delete=models.CASCADE)
#     add_to_sequennce = models.ForeignKey(Sequence, blank=True, null=True)

# class SequenceSubscription(BaseModel):
#     person = models.ForeignKey(Person, on_delete=models.CASCADE)
#     sequence = models.ForeignKey(Sequence, on_delete=models.CASCADE)

# class SequenceTombstone(BaseModel):
#     person = models.ForeignKey(Person, on_delete=models.CASCADE)
#     sequence = models.ForeignKey(Sequence, on_delete=models.CASCADE)
#     started_at = models.DateTimeField(blank=True, null=True, default=timezone.now)
#     completed_at = models.DateTimeField(blank=True, null=True, default=timezone.now)

# class SequenceStepTombstone(BaseModel):
#     person = models.ForeignKey(Person, on_delete=models.CASCADE)
#     sequence_step = models.ForeignKey(SequenceStep, on_delete=models.CASCADE)
#     started_at = models.DateTimeField(blank=True, null=True, default=timezone.now)
#     completed_at = models.DateTimeField(blank=True, null=True, default=timezone.now)


# class MessageTrigger(BaseModel):
#     message = models.ForeignKey(Message, blank=True, null=True, on_delete=models.SET_NULL)

#     send_after_local_tz = models.DateTimeField(blank=True, null=True, default=timezone.now)
#     send_after_server_tz = models.DateTimeField(blank=True, null=True, default=timezone.now)
#     send_after_message = models.DateTimeField(blank=True, null=True, default=timezone.now)
#     send_after_message = models.DateTimeField(blank=True, null=True, default=timezone.now)
#     subscription = models.ForeignKey(Subscription, blank=True, null=True)

#     # conditions ->  MessageTriggerCondition_set

# class MessageTriggerCondition(BaseModel):
#     message_trigger = models.ForeignKey(MessageTrigger)
#     field = models.CharField(max_length=254)  # subscription.last_last action
#     comparison = models.CharField(max_length=254)   # =, !=, <, >
#     value = models.CharField(max_length=254)  # datetime

#     # action_type = models.CharField(max_length=254)
#     # action_target = models.CharField(max_length=254)
#     # target_message = models.ForeignKey(Message, blank=True, null=True, on_delete=models.SET_NULL)
#     # target_page = models.ForeignKey(Page, blank=True, null=True, on_delete=models.SET_NULL)


# class EmailTombstone(BaseModel):
#     person = models.ForeignKey(Person, on_delete=models.SET_NULL)
#     message = models.ForeignKey(Message, on_delete=models.SET_NULL)
#     trigger = models.ForeignKey(Trigger, on_delete=models.SET_NULL)
#     sent_at = models.DateTimeField(blank=True, null=True, default=timezone.now)

#     encrypted_email = models.TextField(blank=True, null=True)
#     encrypted_message_subject = models.TextField(blank=True, null=True)
#     encrypted_message_body = models.TextField(blank=True, null=True)
