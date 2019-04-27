import logging
import json

from django_hosts.resolvers import reverse
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


class TestHardBounceBasics(MockRequestsTestCase):

    def setUp(self, *args, **kwargs):
        super(TestHardBounceBasics, self).setUp(*args, **kwargs)

    def test_hard_bounce_marks_hard_bounced(self):
        s = Factory.subscription()
        p = s.person

        self.assertEquals(p.hard_bounced, False)
        self.assertEquals(p.hard_bounced_at, None)
        self.assertEquals(p.hard_bounced_message, None)

        bounce_reason = Factory.rand_text()
        p.hard_bounce(bounce_reason)

        self.assertEquals(p.hard_bounced, True)
        self.assertEquals(p.hard_bounced_at, None)
        self.assertEquals(p.hard_bounce_reason, bounce_reason)

    def test_hard_bounce_repeated_leaves_hard_bounced(self):
        s = Factory.subscription()
        p = s.person

        self.assertEquals(p.hard_bounced, False)
        self.assertEquals(p.hard_bounced_at, None)
        self.assertEquals(p.hard_bounced_message, None)

        bounce_reason = Factory.rand_text()
        p.hard_bounce(bounce_reason)
        self.assertEquals(p.hard_bounced, True)
        self.assertNotEquals(p.hard_bounced_at, None)
        self.assertEquals(p.hard_bounce_reason, bounce_reason)
        first_ban_at = p.hard_bounced_at

        new_bounce_reason = Factory.rand_text()
        p.hard_bounce(new_bounce_reason)
        self.assertEquals(p.hard_bounced, True)
        self.assertNotEquals(p.hard_bounced_at, first_ban_at)
        self.assertEquals(p.hard_bounce_reason, new_bounce_reason)

    def test_hard_bounce_stores_event_in_archive(self):
        s = Factory.subscription()
        p = s.person
        m = Factory.message()
        bounce_reason = Factory.rand_text()
        p.hard_bounce(reason=bounce_reason, message=m)

        self.assertEquals(HistoricalEvent.objects.count(), 1)
        h = HistoricalEvent.objects.all()[0]
        self.assertEquals(h.event_type, "hard_bounce")
        self.assertEquals(h.event_creator_type, "person")
        self.assertEquals(h.event_creator_pk, p.pk)
        self.assertEquals(h.event_creator_data, {
            "person": p.get_data_dict(),
            "reason": bounce_reason,
            "message": m.get_data_dict(),
        })
