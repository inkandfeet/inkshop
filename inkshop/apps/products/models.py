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
from django.utils import timezone

from utils.models import HashidBaseModel, HasJWTBaseModel
from utils.encryption import encrypt, decrypt, lookup_hash


class Product(HashidBaseModel):
    name = models.CharField(max_length=512)
    number_of_days = models.IntegerField(blank=True, null=True,)

    def __str__(self):
        return self.name


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
            return "Purchase of %s by %s on %s" % (self.product, self.person, self.created_at)
        except:
            return "Purchase of unknown by unknown on %s" % (self.created_at, )

    @property
    def journeys(self):
        return Journey.objects.filter(productpurchase=self).all().order_by("-start_date")

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



class JourneyDay(HashidBaseModel):
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE)
    day_number = models.IntegerField()
    start_date = models.DateTimeField(blank=True, null=True, default=timezone.now)
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


@receiver(post_save, sender=Journey)
def create_journey_days(sender, instance, created, **kwargs):
    """Create a matching profile whenever a user object is created."""
    if created: 
        for i in range(0, instance.product.number_of_days):
            JourneyDay.objects.create(
                day_number=i+1,
                journey=instance,
            )