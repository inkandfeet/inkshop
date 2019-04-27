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
from django.template.loader import render_to_string
from django.contrib.auth.signals import user_logged_in
from utils.helpers import reverse
from django.utils.functional import cached_property
from django.utils import timezone

from utils.models import HashidBaseModel, HasJWTBaseModel
from utils.encryption import encrypt, decrypt, lookup_hash


class UserManager(BaseUserManager):
    def get_by_natural_key(self, username):
        return self.get(hashed_email=lookup_hash(username))

    def create_user(self, email, password=None):
        u = self.create(hashed_email=lookup_hash(email))
        u.email = email
        u.set_password(password)
        u.save()
        return u

    def create_superuser(self, email, password):
        return self.create_user(email, password)


class StaffMember(AbstractBaseUser, HasJWTBaseModel):
    user_type = "user"
    USERNAME_FIELD = "hashed_email"

    encrypted_first_name = models.CharField(max_length=254, blank=True, null=True)
    encrypted_last_name = models.CharField(max_length=254, blank=True, null=True)
    encrypted_email = models.CharField(unique=True, max_length=1024, blank=True, null=True, verbose_name="Email")
    hashed_first_name = models.CharField(max_length=254, blank=True, null=True)
    hashed_last_name = models.CharField(max_length=254, blank=True, null=True)
    hashed_email = models.CharField(unique=True, max_length=1024, blank=True, null=True,)
    email_verified = models.BooleanField(default=False)
    time_zone = models.CharField(max_length=254, blank=True, null=True,)

    staff_flag = models.BooleanField(default=False)
    must_reset_password = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    was_imported = models.BooleanField(default=False)
    was_imported_at = models.DateTimeField(blank=True, null=True)
    import_source = models.CharField(max_length=254, blank=True, null=True)

    objects = UserManager()

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

    def gdpr_dump(self):
        raise NotImplementedError("Haven't implemented GPDR dump yet")
