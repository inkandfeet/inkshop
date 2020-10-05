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
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.contrib.auth.signals import user_logged_in
from utils.helpers import reverse
from django.utils.functional import cached_property
from django.utils.text import slugify
from django.utils import timezone

from utils.models import HashidBaseModel, HasJWTBaseModel
from utils.encryption import encrypt, decrypt, lookup_hash


class Product(HashidBaseModel):
    name = models.CharField(max_length=512)
    slug = models.CharField(max_length=254, blank=True, null=True)
    number_of_days = models.IntegerField(blank=True, null=True,)
    journey_noun = models.CharField(max_length=512)
    has_epilogue = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.name and not self.slug:
            self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    @cached_property
    def share_link(self):
        return "https://share.inkandfeet.com/"


class ProductDay(HashidBaseModel):
    # name = models.CharField(max_length=512)
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    day_number = models.IntegerField(blank=True, null=True,)
    template = models.TextField(blank=True, null=True,)

    def __str__(self):
        return "%s - Day %s" % (self.product, self.day_number)


class Purchase(HashidBaseModel):
    person = models.ForeignKey('people.Person', on_delete=models.CASCADE, blank=True, null=True)
    total = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    discount_code = models.CharField(max_length=254, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    def __str__(self):
        try:
            return "Purchase by %s on %s" % (self.person, self.created_at)
        except:
            return "Purchase by unknown on %s" % (self.created_at, )


class ProductPurchase(HashidBaseModel):
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    purchase = models.ForeignKey(Purchase, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        try:
            return "Purchase of %s by %s on %s" % (self.product, self.purchase.person, self.created_at)
        except:
            return "Purchase of unknown by unknown on %s" % (self.created_at, )

    @property
    def journeys(self):
        return Journey.objects.filter(productpurchase=self).all().order_by("-created_at")

class Journey(HashidBaseModel):
    productpurchase = models.ForeignKey(ProductPurchase, null=True, on_delete=models.SET_NULL, blank=True)
    start_date = models.DateField(blank=True, default=timezone.now, null=True)

    def __str__(self):
        return "%s - %s @ %s" % (self.product, self.productpurchase, self.start_date)

    @cached_property
    def product(self):
        if self.productpurchase:
            return self.productpurchase.product
        return None

    @property
    def days(self):
        return JourneyDay.objects.filter(journey=self).all().order_by("day_number")

    @cached_property
    def journey_num(self):
        index = 0
        for j in self.productpurchase.journey_set.all().order_by("start_date"):
            index += 1
            if j.pk == self.pk:
                return index
        return index

    @cached_property
    def journey_noun(self):
        return self.productpurchase.product.journey_noun

    @cached_property
    def discount_code(self):
        return "asdlkfjdsaf"

    @cached_property
    def discount_code_amount(self):
        return 30


class JourneyDay(HashidBaseModel):
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE)
    day_number = models.IntegerField()
    start_date = models.DateTimeField(blank=True, null=True, default=timezone.now)
    last_user_action = models.DateTimeField(blank=True, null=True)
    encrypted_data = models.TextField(blank=True, null=True,)
    # hashed_data = models.CharField(unique=True, max_length=4096, blank=True, null=True, verbose_name="Email")

    @property
    def data(self):
        if not hasattr(self, "_decrypted_data"):
            self._decrypted_data = decrypt(self.encrypted_data)
        return self._decrypted_data

    @data.setter
    def data(self, value):
        self.encrypted_data = encrypt(value)
        # self.hashed_email = lookup_hash(value)

    @cached_property
    def productday(self):
        return self.journey.product.productday_set.all().filter(day_number=self.day_number)[0]


    @cached_property
    def visible(self):
        if not self.journey.product.has_epilogue or self.day_number < self.journey.days.count():
            return True
        if self.journey.days.get(day_number=self.day_number-1).last_user_action:
            return True

        return False

    @cached_property
    def available(self):
        if self.day_number == 1 or self.journey.days.get(day_number=self.day_number-1).last_user_action:
            return True

        return False


    @cached_property
    def is_epilogue(self):
        if not self.journey.product.has_epilogue or self.day_number < self.journey.days.count():
            return False
        return True


@receiver(post_save, sender=Journey)
def create_journey_days(sender, instance, created, **kwargs):
    """Create a matching profile whenever a user object is created."""
    if created: 
        for i in range(0, instance.product.number_of_days):
            JourneyDay.objects.create(
                day_number=i+1,
                journey=instance,
            )