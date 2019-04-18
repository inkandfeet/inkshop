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


class TestSendToNewsletterGroup(MockRequestsTestCase):

    def setUp(self, *args, **kwargs):
        # Create 3 newsletters
        self.newsletter = Factory.newsletter()
        # Create 5-10 subscribers for each

        # Create 5-15 people not subscribed to either

        super(TestPostSubscribes, self).setUp(*args, **kwargs)

    def test_sends_to_everyone_in_list(self):
        self.assertEquals(False, "Test written")

    def test_does_not_send_to_everyone_not_in_list(self):
        self.assertEquals(False, "Test written")

    def test_if_called_multiple_times_only_sends_once(self):
        self.assertEquals(False, "Test written")

    def test_if_scheduled_for_future_does_not_send(self):
        self.assertEquals(False, "Test written")

    def test_if_scheduled_for_past_sends_immediately(self):
        self.assertEquals(False, "Test written")
