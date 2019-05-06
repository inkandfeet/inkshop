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
from utils.helpers import reverse
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


class Template(BaseModel):
    name = models.CharField(max_length=254)
    raw_html = models.TextField(blank=True, null=True)


class Post(BaseModel):
    name = models.CharField(max_length=254)
    raw_markdown = models.TextField(blank=True, null=True)
    slug = models.CharField(max_length=1024)
    title = models.CharField(max_length=254)
    description = models.CharField(max_length=254, blank=True, null=True)
    template = models.ForeignKey(Template, blank=True, null=True)
    publish_date = models.DateTimeField(blank=True, null=True)
    published = models.BooleanField(default=False)
    private = models.BooleanField(default=False)

    context = models.TextField(blank=True, null=True)  # For location, etc.

    header_image = models.ImageField(
        verbose_name="Header Image",
        upload_to='post-headers',
        blank=True,
        null=True,
    )

    # # related_piece_1: "letter-december-20-grateful"
    # posts:
    # - twitter:
    #     content: I'll be making some changes around here, and releasing a new open-source project.  And I owe that to some ants.
    #     image: header.jpg
    #     publication_plus_days: 0
    #     time: 07:00
    # - facebook:
    #     content: I'll be making some changes around here, and releasing a new open-source project.  And I owe that to some ants.
    #     image: header.jpg
    #     publication_plus_days: 0
    #     time: 07:00
    # - twitter:
    #     content: The best thing I saw this week was the story of where some of our favorite board games come from. https://www.youtube.com/watch?v=ZzACrQevj6k  # noqa 
    #     image: false
    #     publication_plus_days: 3
    #     time: 07:00
    # - facebook:
    #     content: The best thing I saw this week was the story of where some of our favorite board games come from. https://www.youtube.com/watch?v=ZzACrQevj6k  # noqa 
    #     publication_plus_days: 4
    #     time: 07:00
