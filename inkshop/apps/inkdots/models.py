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
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils import timezone

from people.models import Person
from utils.models import BaseModel


class Action(BaseModel):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=254)
    action_target = models.CharField(max_length=254)
    target_message = models.ForeignKey('inkmail.Message', blank=True, null=True, on_delete=models.SET_NULL)
    target_page = models.ForeignKey('website.Page', blank=True, null=True, on_delete=models.SET_NULL)


class MessageHeart(BaseModel):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    message = models.ForeignKey('inkmail.Message', blank=True, null=True, on_delete=models.SET_NULL)


class Device(BaseModel):
    fingerprint = models.CharField(max_length=255, db_index=True)
    hardware_family = models.CharField(max_length=255, blank=True, null=True)
    hardware_brand = models.CharField(max_length=255, blank=True, null=True)
    os = models.CharField(max_length=255, blank=True, null=True)
    browser = models.CharField(max_length=255, blank=True, null=True)
    width = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    is_mobile = models.NullBooleanField(db_index=True, blank=True, null=True)
    is_tablet = models.NullBooleanField(blank=True, null=True)
    is_desktop = models.NullBooleanField(db_index=True, blank=True, null=True)
    is_touch_capable = models.NullBooleanField(blank=True, null=True)
    is_bot = models.NullBooleanField(blank=True, null=True)


class PageHeart(BaseModel):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, blank=True, null=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, blank=True, null=True)
    page = models.ForeignKey('website.Page', blank=True, null=True, on_delete=models.SET_NULL)


class PageView(BaseModel):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    page = models.ForeignKey('website.Page', blank=True, null=True, on_delete=models.SET_NULL)
    url = models.TextField(blank=True, null=True)

    @cached_property
    def opt_out_link(self):
        return "%s%s" % (settings.API_ENDPOINT, reverse("people:opt_out", args=(self.opt_out_key,)))
