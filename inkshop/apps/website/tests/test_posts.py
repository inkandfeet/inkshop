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

t = get_template("inkdots/_page_dots.html")
inkdots_template = t.render({})


class TestPostTemplateRendering(MockRequestsTestCase):

    def test_post_renders(self):
        self.post = Factory.post()
        rendered = self.post.rendered
        self.assertNotEquals(self.post, None)
        self.assertNotEquals(rendered, None)

    def test_full_field_post_renders(self):
        t = Factory.template(content='{{rendered_post_html|safe}}')
        self.post = Factory.post(
            template=t,
        )
        rendered = self.post.rendered
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
    <meta property="og:image" content="" />
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
        window.inkshop.site_data;
    </script>
    %(inkdots)s
</head>

<body >
    %(nav)s
    <p>%(content)s</p>

    %(footer)s
    %(js)s
</body>
</html>""" % {
            "title": self.post.title,
            "description": self.post.description,
            "nav": self.post.template.nav,
            "content": self.post.raw_markdown,
            "footer": self.post.template.footer,
            "css": self.post.template.css,
            "js": self.post.template.js,
            "html_extra_classes": self.post.template.html_extra_classes,
            "body_override": self.post.template.body_override,
            "inkdots": inkdots_template,
        }
        self.assertEquals(rendered, expected_render)
