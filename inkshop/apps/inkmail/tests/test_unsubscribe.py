import logging
import json

from django.urls import reverse
from django.core import mail
from django.conf import settings
from django.test.utils import override_settings

from people.models import Person
from inkmail.models import Subscription
from utils.factory import Factory
from utils.test_helpers import MockRequestsTestCase
from utils.encryption import normalize_lower_and_encrypt, normalize_and_encrypt, encrypt, decrypt
import mock
import unittest


@unittest.skip("For Friday")
class TestUnsubscribeBasics(MockRequestsTestCase):

    def setUp(self, *args, **kwargs):
        self.newsletter = Factory.newsletter()
        super(TestUnsubscribeBasics, self).setUp(*args, **kwargs)

    def test_unsubscribe_link_included_in_every_message_send(self):
        self.assertEquals(False, "Test written")

    def test_newsletter_footer_included_in_every_message_send(self):
        self.assertEquals(False, "Test written")

    def test_transactional_footer_included_in_every_transactional_send(self):
        self.assertEquals(False, "Test written")

    def test_clicking_unsubscribe_marks_unsubscribe(self):
        self.assertEquals(False, "Test written")

    def test_clicking_unsubscribe_prevents_future_mailings(self):
        self.assertEquals(False, "Test written")


@unittest.skip("For Friday")
class TestUnsubscribeResubscribe(MockRequestsTestCase):

    def setUp(self, *args, **kwargs):
        self.newsletter = Factory.newsletter()
        super(TestUnsubscribeBasics, self).setUp(*args, **kwargs)

    def test_unsubscribe_resubscribe_allows_messages_sent(self):
        self.assertEquals(False, "Test written")

    def test_unsubscribe_resubscribe_updates_all_fields(self):
        self.assertEquals(False, "Test written")

    def test_unsubscribe_resubscribe_has_records_of_all_actions(self):
        self.assertEquals(False, "Test written")
