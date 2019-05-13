import logging
import json

from utils.helpers import reverse
from django.core import mail
from django.conf import settings
from django.test.utils import override_settings
from django.template.loader import render_to_string, get_template

from people.models import Person
from archives.models import HistoricalEvent
from inkmail.models import Subscription, OutgoingMessage
from inkmail.tasks import process_outgoing_message_queue
from utils.factory import Factory
from utils.test_helpers import MockRequestsTestCase
from utils.encryption import normalize_lower_and_encrypt, normalize_and_encrypt, encrypt, decrypt
import mock
import unittest


class TestPageTemplateRendering(MockRequestsTestCase):

    def test_page_renders(self):
        self.page = Factory.page()
        rendered = self.page.rendered
        self.assertNotEquals(self.page, None)
        self.assertNotEquals(rendered, None)

    def test_basic_no_frills_page_renders(self):
        t = Factory.template(
            everything_override="This is as basic as it gets.",
        )
        self.page = Factory.page(
            template=t,
        )
        rendered = self.page.rendered
        self.assertEquals(rendered, """This is as basic as it gets.""")

    def test_basic_body_override_page_renders(self):
        t = Factory.template(
            body_override=Factory.rand_text(),
        )
        self.page = Factory.page(
            template=t,
        )
        rendered = self.page.rendered
        self.assertEquals(rendered, """<!doctype html >
<html itemscope itemtype="http://schema.org/CreativeWork" class="%(html_extra_classes)s" lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    <meta name="viewport" content="initial-scale=1, maximum-scale=1, user-scalable=no, width=device-width">
    <title>%(title)s</title>
    <meta name="description" content="%(description)s">


    <!-- Open Graph data -->
    <meta property="og:title" content="%(title)s" />
    <meta property="og:type" content="article" />
    <meta property="og:url" content="" />
    <meta property="og:image" content="https://inkandfeet.com/" />
    <meta property="og:description" content="%(description)s" />
    <meta property="og:site_name" content="" />
    <link rel="canonical" href="" />
    <meta property="article:published_time" content="" />
    <meta property="article:modified_time" content="" />
    <meta property="article:section" content="Writing" />
    <meta property="article:tag" content="Writing" />

    <!-- Schema.org markup for Google+ -->
    <meta itemprop="name" content="%(title)s">
    <meta itemprop="description" content="%(description)s">
    <meta itemprop="author" content="">
    <meta itemprop="provider" content="">


    %(css)s


    <script>
        window.inkshop = window.inkshop || {};
        window.inkshop.page_url = "";
        window.inkshop.site_data_url = "";
        window.inkshop.site_data;
    </script>
</head>

<body >
    %(body_override)s
    %(js)s
</body>
</html>""" % {
            "title": self.page.title,
            "description": self.page.description,
            "css": self.page.template.css,
            "js": self.page.template.js,
            "html_extra_classes": self.page.template.html_extra_classes,
            "body_override": self.page.template.body_override,
        })

    def test_full_field_page_renders(self):
        t = Factory.template(content='{{rendered_page_html|safe}}')
        self.page = Factory.page(
            template=t,
        )
        rendered = self.page.rendered
        expected_render = """<!doctype html >
<html itemscope itemtype="http://schema.org/CreativeWork" class="%(html_extra_classes)s" lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    <meta name="viewport" content="initial-scale=1, maximum-scale=1, user-scalable=no, width=device-width">
    <title>%(title)s</title>
    <meta name="description" content="%(description)s">


    <!-- Open Graph data -->
    <meta property="og:title" content="%(title)s" />
    <meta property="og:type" content="article" />
    <meta property="og:url" content="" />
    <meta property="og:image" content="https://inkandfeet.com/" />
    <meta property="og:description" content="%(description)s" />
    <meta property="og:site_name" content="" />
    <link rel="canonical" href="" />
    <meta property="article:published_time" content="" />
    <meta property="article:modified_time" content="" />
    <meta property="article:section" content="Writing" />
    <meta property="article:tag" content="Writing" />

    <!-- Schema.org markup for Google+ -->
    <meta itemprop="name" content="%(title)s">
    <meta itemprop="description" content="%(description)s">
    <meta itemprop="author" content="">
    <meta itemprop="provider" content="">


    %(css)s


    <script>
        window.inkshop = window.inkshop || {};
        window.inkshop.page_url = "";
        window.inkshop.site_data_url = "";
        window.inkshop.site_data;
    </script>
</head>

<body >
    %(nav)s
    %(content)s
    %(footer)s
    %(js)s
</body>
</html>""" % {
            "title": self.page.title,
            "description": self.page.description,
            "nav": self.page.template.nav,
            "content": self.page.source_text,
            "footer": self.page.template.footer,
            "css": self.page.template.css,
            "js": self.page.template.js,
            "html_extra_classes": self.page.template.html_extra_classes,
            "body_override": self.page.template.body_override,
        }
        self.assertEquals(rendered, expected_render)
