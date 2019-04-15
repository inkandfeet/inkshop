import logging
import json

from django.urls import reverse
from django.core import mail
from django.conf import settings
from django.test.utils import override_settings

from binascii import hexlify, unhexlify
from simplecrypt import encrypt, decrypt

from utils.factory import Factory
from utils.test_helpers import MockRequestsTestCase
import mock


class TestTestHarness(MockRequestsTestCase):

    def tests_run(self):
        self.assertEquals(1 + 1, 2)
