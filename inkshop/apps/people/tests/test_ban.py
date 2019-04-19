import logging
import json

from django.urls import reverse
from django.core import mail
from django.conf import settings
from django.test.utils import override_settings

from people.models import Person
from inkmail.models import Subscription
from history.models import HistoricalEvent
from utils.factory import Factory
from utils.test_helpers import MockRequestsTestCase
from utils.encryption import normalize_lower_and_encrypt, normalize_and_encrypt, encrypt, decrypt
import mock
import unittest


class TestBanBasics(MockRequestsTestCase):

    def setUp(self, *args, **kwargs):
        super(TestBanBasics, self).setUp(*args, **kwargs)

    def test_ban_marks_banned(self):
        s = Factory.subscription()
        p = s.person

        self.assertEquals(p.banned, False)
        self.assertEquals(p.banned_at, None)

        p.ban()

        self.assertEquals(p.banned, True)
        self.assertNotEquals(p.banned_at, None)

    def test_ban_repeated_leaves_banned(self):
        s = Factory.subscription()
        p = s.person

        self.assertEquals(p.banned, False)
        self.assertEquals(p.banned_at, None)

        p.ban()
        self.assertEquals(p.banned, True)
        self.assertNotEquals(p.banned_at, None)
        first_ban_at = p.banned_at

        p.ban()
        self.assertEquals(p.banned, True)
        self.assertNotEquals(p.banned_at, first_ban_at)

    def test_stores_event_in_archive(self):
        s = Factory.subscription()
        p = s.person
        self.assertEquals(HistoricalEvent.objects.count(), 0)
        reason = Factory.rand_str()
        p.ban(reason)

        self.assertEquals(HistoricalEvent.objects.count(), 1)
        h = HistoricalEvent.objects.all()[0]
        self.assertEquals(h.event_type, "ban")
        self.assertEquals(h.event_creator_type, "test")
        self.assertEquals(h.event_creator_pk, 1)
        self.assertEquals(h.event_creator_data, {
            "person": p.get_data_dict(),
            "reason": reason,
        })
