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


class TestHistoricalEvents(MailTestCase):

    def setUp(self, *args, **kwargs):
        super(TestHistoricalEvents, self).setUp(*args, **kwargs)

    def test_core_fields(self):
        self.assertEquals(True, "Test written")


@override_settings(DISABLE_ENCRYPTION_FOR_TESTS=False)
class TestHistoricalBasicEncryptionHarness(MailTestCase):

    def test_basic_encryption(self):
        e = Factory.rand_str()
        historical_event = HistoricalEvent.objects.create()
        historical_event.event_data = e
        historical_event.save()
        self.assertEquals(historical_event.event_data, e)

        e = "😀💌❤️"
        historical_event = HistoricalEvent.objects.create()
        historical_event.event_data = e
        historical_event.save()
        self.assertEquals(historical_event.event_data, e)

        e = Factory.rand_text()
        historical_event = HistoricalEvent.objects.create()
        historical_event.event_data = e
        historical_event.save()
        self.assertEquals(historical_event.event_data, e)

        e = Factory.rand_email()
        historical_event = HistoricalEvent.objects.create()
        historical_event.event_data = e
        historical_event.save()
        self.assertEquals(historical_event.event_data, e)


@override_settings(DISABLE_ENCRYPTION_FOR_TESTS=False)
class TestHistoricalEncryptionHarnessForOddTypes(MailTestCase):

    def test_extended_types_encryption(self):
        e = Factory.rand_phone()
        historical_event = HistoricalEvent.objects.create()
        historical_event.event_data = e
        historical_event.save()
        self.assertEquals(historical_event.event_data, e)

        e = Factory.rand_name()
        historical_event = HistoricalEvent.objects.create()
        historical_event.event_data = e
        historical_event.save()
        self.assertEquals(historical_event.event_data, e)

        e = Factory.temp_password()
        historical_event = HistoricalEvent.objects.create()
        historical_event.event_data = e
        historical_event.save()
        self.assertEquals(historical_event.event_data, e)

        e = Factory.rand_url()
        historical_event = HistoricalEvent.objects.create()
        historical_event.event_data = e
        historical_event.save()
        self.assertEquals(historical_event.event_data, e)


@override_settings(DISABLE_ENCRYPTION_FOR_TESTS=False)
class TestHistoricalEncryptionHarnessForObjects(MailTestCase):

    def test_extended_types_encryption(self):
        e = {
            "a": Factory.rand_phone(),
            "b": Factory.rand_phone(),
            "c": Factory.temp_password(),
        }
        historical_event = HistoricalEvent.objects.create()
        historical_event.event_data = e
        historical_event.save()
        self.assertEquals(historical_event.event_data, e)

        e = {
            "a": Factory.rand_name(),
            "b": Factory.rand_phone(),
            "c": Factory.rand_name(),
        }
        historical_event = HistoricalEvent.objects.create()
        historical_event.event_data = e
        historical_event.save()
        self.assertEquals(historical_event.event_data, e)

        e = {
            "a": Factory.temp_password(),
            "q": Factory.rand_phone(),
            "l": settings,
        }
        historical_event = HistoricalEvent.objects.create()
        historical_event.event_data = e
        historical_event.save()
        self.assertEquals(historical_event.event_data, e)

        e = {
            "p": Factory.rand_url(),
            "r": Factory.rand_rand_phoneurl(),
            "a": Factory.temp_password(),
        }
        historical_event = HistoricalEvent.objects.create()
        historical_event.event_data = e
        historical_event.save()
        self.assertEquals(historical_event.event_data, e)
