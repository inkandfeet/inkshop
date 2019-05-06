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


class TestPostTemplateRendering(MockRequestsTestCase):

    def test_post_renders(self):
        self.post = Factory.post()
        rendered = self.post.rendered
        self.assertNotEquals(self.post, None)
        self.assertNotEquals(rendered, None)

    def test_full_field_post_renders(self):
        t = Factory.template()
        self.post = Factory.post(
            template=t,
        )
        url = reverse('website:page_or_post', kwargs={"page_slug": self.post.slug, },)
        response = self.get(url)
        self.assertEquals(response.status_code, 200)
        resp_content = str(response.content)

        self.assertIn(self.post.title, resp_content)
        self.assertIn(self.post.description, resp_content)
        self.assertIn(self.post.template.nav, resp_content)
        self.assertIn(self.post.raw_markdown, resp_content)
        self.assertIn(self.post.template.footer, resp_content)
        self.assertIn(self.post.template.css, resp_content)
        self.assertIn(self.post.template.js, resp_content)
        if self.post.template.body_override:
            self.assertIn(self.post.template.body_override, resp_content)


class TestPageTemplateRendering(MockRequestsTestCase):

    def test_page_renders(self):
        self.page = Factory.page()
        rendered = self.page.rendered
        self.assertNotEquals(self.page, None)
        self.assertNotEquals(rendered, None)

    def test_full_field_page_renders(self):
        t = Factory.template()
        self.page = Factory.page(
            template=t,
        )
        url = reverse('website:page_or_post', kwargs={"page_slug": self.page.slug, },)
        response = self.get(url)
        self.assertEquals(response.status_code, 200)
        resp_content = str(response.content)

        self.assertIn(self.page.title, resp_content)
        self.assertIn(self.page.description, resp_content)
        self.assertIn(self.page.template.nav, resp_content)
        self.assertIn(self.page.source_text, resp_content)
        self.assertIn(self.page.template.footer, resp_content)
        self.assertIn(self.page.template.css, resp_content)
        self.assertIn(self.page.template.js, resp_content)
        if self.page.template.body_override:
            self.assertIn(self.page.template.body_override, resp_content)
