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
from utils.helpers import reverse
from django.utils.functional import cached_property
from django.utils import timezone

from utils.models import HashidBaseModel, HasJWTBaseModel
from utils.encryption import encrypt, decrypt, lookup_hash


class Product(HashidBaseModel):
    name = models.CharField(max_length=512)

    def __str__(self):
        return self.name


class Purchase(HashidBaseModel):
    person = models.ForeignKey('people.Person', on_delete=models.CASCADE, blank=True, null=True)
    total = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    discount_code = models.CharField(max_length=254, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return "Purchase by %s on %s" % (self.person, self.created_at)


class ProductPurchase(HashidBaseModel):
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    purchase = models.ForeignKey(Purchase, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return "Purchase of %s by %s" % (self.product, self.purchase.person)


class Journey(HashidBaseModel):
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL, blank=True)
    productpurchase = models.ForeignKey(ProductPurchase, null=True, on_delete=models.SET_NULL, blank=True)
    start_date = models.DateField(blank=True, default=timezone.now, null=True)

    def __str__(self):
        return "%s - %s @ %s" % (self.product, self.productpurchase, self.start_date)
