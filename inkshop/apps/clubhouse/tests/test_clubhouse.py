import logging
import json

from utils.helpers import reverse
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
from archives.models import HistoricalEvent


@unittest.skip("Add these once the clubhouse UI stabilizes")
class TestClubhouseLoads(MailTestCase):

    def setUp(self, *args, **kwargs):
        super(TestClubhouseLoads, self).setUp(*args, **kwargs)

    def test_core_fields(self):
        self.assertEquals(True, "Test written")
