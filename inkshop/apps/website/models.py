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
from django_hosts.resolvers import reverse
from django.utils.functional import cached_property
from django.utils import timezone

from utils.models import BaseModel


class Page(BaseModel):
    slug = models.CharField(max_length=254)
    hash_id = models.CharField(max_length=254)
    title = models.CharField(max_length=254)
    description = models.CharField(max_length=254, blank=True, null=True)
    keywords = models.CharField(max_length=254, blank=True, null=True)
    source_text = models.TextField(blank=True, null=True)
    rendered_html = models.TextField(blank=True, null=True)
