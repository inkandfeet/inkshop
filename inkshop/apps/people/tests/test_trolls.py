import logging
import json

from django.urls import reverse
from django.core import mail
from django.conf import settings
from django.test.utils import override_settings

from people.models import Person
from inkmail.models import Subscription
from archives.models import HistoricalEvent
from utils.factory import Factory
from utils.test_helpers import MockRequestsTestCase
from utils.encryption import normalize_lower_and_encrypt, normalize_and_encrypt, encrypt, decrypt
import mock
import unittest


class TestTrollBasics(MockRequestsTestCase):

    def setUp(self, *args, **kwargs):
        super(TestTrollBasics, self).setUp(*args, **kwargs)

    def test_troll_marks_trolled(self):
        s = Factory.subscription()
        p = s.person

        self.assertEquals(p.marked_troll, None)
        self.assertEquals(p.marked_troll_at, None)

        p.mark_troll()

        self.assertEquals(p.marked_troll, True)
        self.assertNotEquals(p.marked_troll_at, None)

    def test_troll_repeated_leaves_trolled(self):
        s = Factory.subscription()
        p = s.person

        self.assertEquals(p.marked_troll, None)
        self.assertEquals(p.marked_troll_at, None)

        p.mark_troll()
        self.assertEquals(p.marked_troll, True)
        self.assertNotEquals(p.marked_troll_at, None)
        first_troll_at = p.marked_troll_at

        p.mark_troll()
        self.assertEquals(p.marked_troll, True)
        self.assertNotEquals(p.marked_troll_at, first_troll_at)

    def test_stores_event_in_archive(self):
        s = Factory.subscription()
        p = s.person
        p.mark_troll()

        self.assertEquals(HistoricalEvent.objects.count(), 1)
        h = HistoricalEvent.objects.all()[0]
        self.assertEquals(h.event_type, "mark_troll")
        self.assertEquals(h.event_creator_type, "person")
        self.assertEquals(h.event_creator_pk, p.pk)
        self.assertEquals(h.event_creator_data, {
            "person": p.get_data_dict(),
        })
