import datetime
import hashlib
import logging
import jwt
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
from django.template.loader import render_to_string
from django.contrib.auth.signals import user_logged_in
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils import timezone

from utils.models import HashidBaseModel
from utils.encryption import encrypt, decrypt, lookup_hash


class Person(HashidBaseModel):
    encrypted_first_name = models.CharField(max_length=4096, blank=True, null=True)
    encrypted_last_name = models.CharField(max_length=4096, blank=True, null=True)
    encrypted_email = models.CharField(unique=True, max_length=4096, blank=True, null=True,)
    hashed_first_name = models.CharField(max_length=4096, blank=True, null=True)
    hashed_last_name = models.CharField(max_length=4096, blank=True, null=True)
    hashed_email = models.CharField(unique=True, max_length=4096, blank=True, null=True, verbose_name="Email")
    email_verified = models.BooleanField(default=False)
    time_zone = models.CharField(max_length=254, blank=True, null=True,)

    was_imported = models.BooleanField(default=False)
    was_imported_at = models.DateTimeField(blank=True, null=True)
    import_source = models.CharField(max_length=254, blank=True, null=True)

    marked_troll = models.BooleanField(default=False)
    marked_troll_at = models.DateTimeField(blank=True, null=True)
    banned = models.BooleanField(default=False)
    banned_at = models.DateTimeField(blank=True, null=True)
    hard_bounced = models.BooleanField(default=False)
    hard_bounced_at = models.DateTimeField(blank=True, null=True)
    hard_bounced_reason = models.TextField(blank=True, null=True)
    hard_bounced_message = models.ForeignKey('inkmail.Message', blank=True, null=True, on_delete=models.SET_NULL)

    never_contact_set = models.BooleanField(default=False)
    never_contact_set_at = models.DateTimeField(blank=True, null=True)

    personal_contact = models.BooleanField(default=False)

    @property
    def email(self):
        if not hasattr(self, "_decrypted_email"):
            self._decrypted_email = decrypt(self.encrypted_email)
        return self._decrypted_email

    @email.setter
    def email(self, value):
        self.encrypted_email = encrypt(value)
        self.hashed_email = lookup_hash(value)

    @property
    def first_name(self):
        if not hasattr(self, "_decrypted_first_name"):
            self._decrypted_first_name = decrypt(self.encrypted_first_name)
        return self._decrypted_first_name

    @first_name.setter
    def first_name(self, value):
        self.encrypted_first_name = encrypt(value)
        self.hashed_first_name = lookup_hash(value)

    @property
    def last_name(self):
        if not hasattr(self, "_decrypted_last_name"):
            self._decrypted_last_name = decrypt(self.encrypted_last_name)
        return self._decrypted_last_name

    @last_name.setter
    def last_name(self, value):
        self.encrypted_last_name = encrypt(value)
        self.hashed_last_name = lookup_hash(value)

    def ban(self):
        from archives.models import HistoricalEvent
        if not self.banned:
            self.banned = True
            self.banned_at = timezone.now()
            self.save()
            HistoricalEvent.log(person=self, event_type="ban")

    def mark_troll(self):
        from archives.models import HistoricalEvent
        if not self.marked_troll:
            self.marked_troll = True
            self.marked_troll_at = timezone.now()
            self.save()
            HistoricalEvent.log(person=self, event_type="mark_troll")

    def hard_bounce(self, reason=None, bouncing_message=None):
        from archives.models import HistoricalEvent
        if not self.hard_bounced:
            self.hard_bounced = True
            self.hard_bounced_at = timezone.now()
            self.hard_bounced_reason = reason
            self.hard_bounced_message = bouncing_message
            self.save()
            HistoricalEvent.log(person=self, event_type="mark_hard_bounce", reason=reason, message=bouncing_message)

    def gdpr_dump(self):
        raise NotImplementedError("Haven't implemented GPDR dump yet")

    def messages_sent(self):
        return self.outgoingmessage_set.order_by("created_at").all()
