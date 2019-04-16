import logging
import json
import mock

from django.urls import reverse
from django.core import mail
from django.conf import settings
from django.test.utils import override_settings

from utils.factory import Factory
from utils.test_helpers import MockRequestsTestCase
from utils.encryption import normalize_lower_and_encrypt, normalize_and_encrypt, encrypt, decrypt


class TestTestHarness(MockRequestsTestCase):

    def tests_run(self):
        self.assertEquals(1 + 1, 2)


class TestEncryptionHarness(MockRequestsTestCase):

    def test_basic_encryption(self):
        e = Factory.rand_str()
        self.assertEquals(e, decrypt(encrypt(e)))

        e = Factory.rand_text()
        self.assertEquals(e, decrypt(encrypt(e)))

        e = Factory.rand_email()
        self.assertEquals(e, decrypt(encrypt(e)))

        e = Factory.rand_phone()
        self.assertEquals(e, decrypt(encrypt(e)))

        e = Factory.rand_name()
        self.assertEquals(e, decrypt(encrypt(e)))

        e = Factory.temp_password()
        self.assertEquals(e, decrypt(encrypt(e)))

        e = Factory.rand_url()
        self.assertEquals(e, decrypt(encrypt(e)))

    def test_normalize_lower_and_encrypt(self):
        s = "Here's a test of thing!! "
        self.assertEquals(
            "here's a test of thing!!",
            decrypt(normalize_lower_and_encrypt(s))
        )

        s = "   Here's a test of thing!! "
        self.assertEquals(
            "here's a test of thing!!",
            decrypt(normalize_lower_and_encrypt(s))
        )

        s = """   Here's a TEST of thing!!        
"""  # noqa
        self.assertEquals(
            "here's a test of thing!!",
            decrypt(normalize_lower_and_encrypt(s))
        )

    def test_normalize_and_encrypt(self):
        s = "Here's a test of thing!! "
        self.assertEquals(
            "Here's a test of thing!!",
            decrypt(normalize_and_encrypt(s))
        )

        s = "   Here's a test of thing!! "
        self.assertEquals(
            "Here's a test of thing!!",
            decrypt(normalize_and_encrypt(s))
        )

        s = """   Here's a TEST of thing!!        
"""  # noqa
        self.assertEquals(
            "Here's a TEST of thing!!",
            decrypt(normalize_and_encrypt(s))
        )
