import datetime
import extraction
import hashlib
import magic
import mistune
import io
import logging
import random
import requests
import time
from fake_useragent import UserAgent
import uuid
from base64 import b64encode
from io import BytesIO
from PIL import Image, ImageOps
from tempfile import NamedTemporaryFile

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.template import Context
from django.template import Template as DjangoTemplate
from django.template.loader import render_to_string, get_template
from django.utils.html import mark_safe
from utils.helpers import reverse
from django.utils.functional import cached_property
from django.utils import timezone

from inkmail.models import Organization
from utils.models import HashidBaseModel
from utils.encryption import file_hash

markdown = mistune.Markdown()
ua = UserAgent()


class Template(HashidBaseModel):
    name = models.CharField(max_length=254, unique=True)

    nav = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    footer = models.TextField(blank=True, null=True)
    css = models.TextField(blank=True, null=True)
    js = models.TextField(blank=True, null=True)
    html_extra_classes = models.CharField(max_length=255, blank=True, null=True)

    body_override = models.TextField(blank=True, null=True, verbose_name="Body (will overwrite all other fields).")
    everything_override = models.TextField(blank=True, null=True, verbose_name="Entire page (will override everything else)")

    @cached_property
    def context(self):
        return {
            "nav": self.nav,
            "content": self.content,
            "footer": self.footer,
            "css": self.css,
            "js": self.js,
            "html_extra_classes": self.html_extra_classes,
            "body_override": self.body_override,
            "everything_override": self.everything_override,
        }

    def __str__(self):
        return self.name


class Resource(HashidBaseModel):
    name = models.CharField(max_length=254)

    binary_file = models.FileField(blank=True, null=True, upload_to="resources")
    text_file = models.TextField(blank=True, null=True)
    mime_type = models.CharField(max_length=255, blank=True, null=True)
    hashed_filename = models.CharField(max_length=320, blank=True, null=True, db_index=True)
    content_size = models.IntegerField(blank=True, null=True)

    # @cached_property
    @property
    def content(self):
        if self.text_file:
            return self.text_file
        elif self.binary_file:
            return self.binary_file
        return ""

    @property
    def raw_content(self):
        if self.text_file:
            return self.text_file
        elif self.binary_file:
            self.binary_file.open()
            c = self.binary_file.read()
            self.binary_file.close()
            return c
        return ""

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        old_resource = None
        if self.pk:
            old_resource = Resource.objects.get(pk=self.pk)
        super(Resource, self).save(*args, **kwargs)
        needs_resave = False

        if not self.name:
            needs_resave = True
            if self.binary_file:
                self.name = self.binary_file.name
            else:
                self.name = "Unnamed file %s" % self.hashid

        if not self.mime_type:
            if self.text_file or self.binary_file:
                self.mime_type = magic.from_buffer(self.raw_content, mime=True)
                needs_resave = True

        if old_resource:
            split_name = self.name.split(".")
            split_name.insert(-1, file_hash(self.raw_content))
            self.hashed_filename = ".".join(split_name)
            self.content_size = len(self.raw_content)
            if (
                self.hashed_filename != old_resource.hashed_filename
                or self.content_size != old_resource.content_size
            ):
                needs_resave = True

        if needs_resave:
            self.save()


class Page(HashidBaseModel):
    name = models.CharField(max_length=254, unique=True)
    slug = models.CharField(max_length=254, blank=True, null=True)
    root_page = models.BooleanField(default=False)
    title = models.CharField(max_length=1024)
    description = models.CharField(max_length=1024, blank=True, null=True)
    section = models.CharField(max_length=254, blank=True, null=True)
    keywords = models.CharField(max_length=254, blank=True, null=True)
    template = models.ForeignKey(Template, blank=True, null=True, on_delete=models.SET_NULL)
    source_text = models.TextField(blank=True, null=True)
    rendered_html = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.name and not self.slug:
            self.slug = slugify(self.name)
        if self.root_page:
            self.slug = ""
        super(Page, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    # @cached_property
    @property
    def rendered(self,):
        t = get_template(self.template.name)

        o = Organization.get()
        context = self.template.context.copy()
        context.update(**{
            "organization_address": o.address,
            "organization_name": o.name,
            "name": self.name,
            "page_name": self.name,
            "section": self.section,
            "source_text": self.source_text,
            "slug": self.slug,
            "title": self.title,
            "description": self.description,
            "keywords": self.keywords,
            "links": Link.objects.all().order_by("-publish_date", "-created_at"),
        })

        c = Context(context)
        content_template = DjangoTemplate(self.source_text)
        context["rendered_page_html"] = mark_safe(content_template.render(c).encode("utf-8").decode())

        return t.render(context)


class Post(HashidBaseModel):
    name = models.CharField(max_length=254)
    raw_markdown = models.TextField(blank=True, null=True)
    slug = models.CharField(max_length=1024, blank=True, null=True)
    root_page = models.BooleanField(default=False)
    title = models.CharField(max_length=1024)
    description = models.CharField(max_length=1024, blank=True, null=True)
    keywords = models.CharField(max_length=254, blank=True, null=True)
    template = models.ForeignKey(Template, blank=True, null=True, on_delete=models.SET_NULL)
    section = models.CharField(max_length=254, blank=True, null=True)
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

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.root_page:
            self.slug = ""
        if self.name and self.slug is None:
            self.slug = slugify(self.name)
        super(Post, self).save(*args, **kwargs)

    @property
    def rendered(self):
        t = get_template(self.template.name)

        o = Organization.get()
        context = self.template.context.copy()
        context.update(**{
            "organization_address": o.address,
            "organization_name": o.name,
            "name": self.name,
            "page_name": self.name,
            "section": self.section,
            "raw_markdown": self.raw_markdown,
            "slug": self.slug,
            "title": self.title,
            "description": self.description,
            "publish_date": self.publish_date,
            "published": self.published,
            "private": self.private,
            "context": self.context,
            "links": Link.objects.all().order_by("-publish_date", "-created_at"),
        })

        c = Context(context)
        rendered_string = markdown(self.raw_markdown)
        rendered_string = rendered_string.replace(u"’", '&rsquo;').replace(u"“", '&ldquo;')
        rendered_string = rendered_string.replace(u"”", '&rdquo;').replace(u"’", "&rsquo;")

        content_template = DjangoTemplate(rendered_string)
        context["rendered_post_html"] = mark_safe(content_template.render(c).encode("utf-8").decode())

        return t.render(context)

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


class Link(HashidBaseModel):
    name = models.CharField(max_length=254, blank=True, null=True)
    slug = models.CharField(max_length=1024, blank=True, null=True)
    target_url = models.TextField(blank=True, null=True)

    title = models.CharField(max_length=1024, blank=True, null=True)
    description = models.CharField(max_length=1024, blank=True, null=True)
    publish_date = models.DateTimeField(blank=True, null=True)
    published = models.BooleanField(default=False)
    private = models.BooleanField(default=False)
    thumbnail_image_source = models.ImageField(
        verbose_name="Thumbnail Source",
        upload_to='link-images-source',
        blank=True,
        null=True,
    )
    thumbnail_image = models.ImageField(
        verbose_name="Thumbnail",
        upload_to='link-images',
        blank=True,
        null=True,
    )
    destination_title = models.TextField(blank=True, null=True)
    destination_description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.name and not self.slug:
            self.slug = slugify(self.name)
        super(Link, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.name)

    def fetch_metadata_from_target(self):
        try:
            headers = {'User-Agent': str(ua.chrome)}
            r = requests.get(self.target_url, headers=headers)
            content = r.text
            extracted = extraction.Extractor().extract(content, source_url=self.target_url)
            changed = False
            if extracted.title:
                self.destination_title = extracted.title
                if not self.name:
                    self.name = extracted.title
                if not self.title:
                    self.title = extracted.title
                changed = True
            if extracted.description:
                self.destination_description = extracted.description
                if not self.description:
                    self.description = extracted.description
                changed = True
            if extracted.images:
                found_image = False
                now = timezone.now()
                for i in extracted.images:
                    try:
                        print(i)
                        image_request = requests.get(i)
                        source = Image.open(io.BytesIO(image_request.content))
                        thumb = ImageOps.fit(source, (400, 300), Image.ANTIALIAS, 0, (0.5, 0.5))
                        thumb_buffer = BytesIO()
                        thumb.save(thumb_buffer, format="PNG", quality=60)
                        thumb_buffer.seek(0)

                        self.thumbnail_image_source.save(
                            "%s%s-source.jpg" % (
                                self.hashid,
                                now
                            ),
                            ContentFile(image_request.content)
                        )
                        self.thumbnail_image.save(
                            "%s%s-thumb.jpg" % (
                                self.hashid,
                                now
                            ),
                            ContentFile(thumb_buffer.getvalue())
                        )
                        found_image = True
                        break
                    except:
                        import traceback
                        traceback.print_exc()
                        pass

                if found_image:
                    changed = True
            if changed:
                self.save()
        except:
            pass
