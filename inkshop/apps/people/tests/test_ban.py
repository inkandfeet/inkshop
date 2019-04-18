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
class TestBanBasics(MockRequestsTestCase):

    def setUp(self, *args, **kwargs):
        super(TestBanBasics, self).setUp(*args, **kwargs)

    def test_ban_marks_banned(self):
        self.assertEquals(False, "Test written")
