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
from binascii import hexlify, unhexlify
from simplecrypt import encrypt, decrypt

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

from utils.models import BaseModel


class UserManager(BaseUserManager):
    def get_by_natural_key(self, username):
        return self.get(email__iexact=username)

    def create_user(self, email, password=None):
        u = self.create(email=email)
        u.set_password(password)
        u.save()

    def create_superuser(self, email, password):
        return self.create_user(email, password)


class HasJWTBaseModel(BaseModel):
    inkid = models.CharField(blank=True, null=True, max_length=512, unique=True, db_index=True, editable=False)
    salted_inkid = models.CharField(blank=True, null=True, max_length=512, unique=True, db_index=True, editable=False)
    api_jwt_cached = models.CharField(blank=True, null=True, max_length=512, unique=True, editable=False)

    class Meta:
        abstract = True

    def regenerate_api_jwt(self):
        self.api_jwt_cached = jwt.encode({
            'inkid': self.inkid,
            'version': 1,
            'user_type': self.user_type,

        }, settings.JWT_SECRET, algorithm='HS256').decode()

        return self.api_jwt_cached

    @cached_property
    def api_jwt(self):
        if not self.api_jwt_cached:
            self.api_jwt_cached = self.regenerate_api_jwt()
            self.save()

        return self.api_jwt_cached

    @cached_property
    def events(self):
        from events.models import Event
        return Event.objects.filter(creator=self.inkid)

    @cached_property
    def unique_name(self):
        return "%s %s" % (self.adjective.title(), self.noun.title())


class Person(HasJWTBaseModel):
    encrypted_first_name = models.CharField(max_length=254, blank=True, null=True)
    encrypted_last_name = models.CharField(max_length=254, blank=True, null=True)
    encrypted_email = models.CharField(max_length=254, blank=True, null=True,)
    email_verified = models.BooleanField(default=False)
    time_zone = models.CharField(max_length=254, blank=True, null=True,)

    @property
    def email(self):
        return decrypt(settings.ENCRYPTION_KEY, unhexlify(self.encrypted_email)).decode('utf-8')

    @property
    def first_name(self):
        return decrypt(settings.ENCRYPTION_KEY, unhexlify(self.encrypted_first_name)).decode('utf-8')

    @property
    def last_name(self):
        return decrypt(settings.ENCRYPTION_KEY, unhexlify(self.encrypted_last_name)).decode('utf-8')
