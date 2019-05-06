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


class TestTemplateLoader(MockRequestsTestCase):

    def test_template_loads(self):
        self.template = Factory.template()
        t = get_template(self.template.name)
        rendered = t.render({})
        self.assertNotEquals(t, None)
        self.assertNotEquals(rendered, None)

    def test_template_builds(self):
        self.template = Factory.template()
        t = get_template(self.template.name)
        rendered = t.render({})

        self.assertIn(self.template.nav, rendered)
        self.assertIn(self.template.content, rendered)
        self.assertIn(self.template.footer, rendered)
        self.assertIn(self.template.css, rendered)
        self.assertIn(self.template.js, rendered)

    def test_template_body_override_works(self):
        self.template = Factory.template(body_override=Factory.rand_text())

        t = get_template(self.template.name)
        rendered = t.render({})

        self.assertIn(self.template.body_override, rendered)
        self.assertNotIn(self.template.nav, rendered)
        self.assertNotIn(self.template.content, rendered)
        self.assertNotIn(self.template.footer, rendered)
