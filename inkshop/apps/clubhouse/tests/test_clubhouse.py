import logging
import json

from django.urls import reverse
from django.core import mail
from django.conf import settings
from django.test.utils import override_settings

from people.models import Person
from inkmail.models import Subscription
from utils.factory import Factory
from utils.test_helpers import MailTestCase
from utils.encryption import normalize_lower_and_encrypt, normalize_and_encrypt, encrypt, decrypt
import mock
import unittest
from history.models import HistoricalEvent


class TestClubhouseLoads(MailTestCase):

    def setUp(self, *args, **kwargs):
        super(TestClubhouseLoads, self).setUp(*args, **kwargs)

    def test_core_fields(self):
        self.assertEquals(True, "Test written")
