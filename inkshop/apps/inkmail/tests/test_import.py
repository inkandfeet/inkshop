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


class TestNewsletterImport(MockRequestsTestCase):

    def setUp(self, *args, **kwargs):
        # Create 2 banned users
        # Create 3
        self.newsletter = Factory.newsletter()
        # Create 5-10 subscribers for each

        # Create 5-15 people not subscribed to either

        super(TestNewsletterImport, self).setUp(*args, **kwargs)

    def test_import_adds_person_to_newsletter(self):
        s = None
        p = None
        self.assertEquals(False, "Test written")
        self.assertEquals(True, "Person present")
        self.assertEquals(True, "Newsletter present")
        self.assertEquals(True, "Subscription present")
        self.assertEquals(True, "not banned")
        self.assertEquals(True, "not trolled")
        self.assertEquals(s.subscription_url)
        self.assertEquals(s.subscribed_from_ip)
        self.assertEquals(s.double_opted_in)
        self.assertEquals(s.double_opted_in_at)
        self.assertEquals(s.has_set_never_unsubscribe)
        self.assertEquals(s.unsubscribed)
        self.assertEquals(s.unsubscribed_at)

        self.assertEquals(p.email_verified)
        self.assertEquals(p.time_zone)
        self.assertEquals(p.marked_troll)
        self.assertEquals(p.marked_troll_at)
        self.assertEquals(p.banned)
        self.assertEquals(p.banned_at)
        self.assertEquals(p.hard_bounced)
        self.assertEquals(p.hard_bounced_at)
        self.assertEquals(p.hard_bounced_message)
        self.assertEquals(p.never_contact_set)
        self.assertEquals(p.never_contact_set_at)
        self.assertEquals(p.personal_contact)

    def test_import_ignores_banned_people(self):
        self.assertEquals(False, "Test written")

    def test_import_imports_trolls_but_marks_them(self):
        s = None
        p = None
        self.assertEquals(False, "Test written")
        self.assertEquals(True, "Person present")
        self.assertEquals(True, "Newsletter present")
        self.assertEquals(True, "Subscription present")
        self.assertEquals(True, "not banned")
        self.assertEquals(True, "not trolled")
        self.assertEquals(s.subscription_url)
        self.assertEquals(s.subscribed_from_ip)
        self.assertEquals(s.double_opted_in)
        self.assertEquals(s.double_opted_in_at)
        self.assertEquals(s.has_set_never_unsubscribe)
        self.assertEquals(s.unsubscribed)
        self.assertEquals(s.unsubscribed_at)

        self.assertEquals(p.email_verified)
        self.assertEquals(p.time_zone)
        self.assertEquals(p.marked_troll)
        self.assertEquals(p.marked_troll_at)
        self.assertEquals(p.banned)
        self.assertEquals(p.banned_at)
        self.assertEquals(p.hard_bounced)
        self.assertEquals(p.hard_bounced_at)
        self.assertEquals(p.hard_bounced_message)
        self.assertEquals(p.never_contact_set)
        self.assertEquals(p.never_contact_set_at)
        self.assertEquals(p.personal_contact)


@unittest.skip("Once purchases are added in.")
class TestPurchaserImport(MockRequestsTestCase):

    def setUp(self, *args, **kwargs):
        # Create 2 banned users
        # Create 3
        self.newsletter = Factory.newsletter()
        # Create 5-10 subscribers for each

        # Create 5-15 people not subscribed to either

        super(TestPurchaserImport, self).setUp(*args, **kwargs)

    def test_import_adds_person_to_newsletter(self):
        p = None
        self.assertEquals(False, "Test written")
        self.assertEquals(True, "Person present")
        self.assertEquals(True, "Newsletter present")
        self.assertEquals(True, "Subscription present")
        self.assertEquals(True, "not banned")
        self.assertEquals(True, "not trolled")

        self.assertEquals(p.email_verified)
        self.assertEquals(p.time_zone)
        self.assertEquals(p.marked_troll)
        self.assertEquals(p.marked_troll_at)
        self.assertEquals(p.banned)
        self.assertEquals(p.banned_at)
        self.assertEquals(p.hard_bounced)
        self.assertEquals(p.hard_bounced_at)
        self.assertEquals(p.hard_bounced_message)
        self.assertEquals(p.never_contact_set)
        self.assertEquals(p.never_contact_set_at)
        self.assertEquals(p.personal_contact)

    def test_import_ignores_banned_people(self):
        self.assertEquals(False, "Test written")

    def test_import_imports_trolls_but_marks_them(self):
        p = None
        self.assertEquals(False, "Test written")
        self.assertEquals(True, "Person present")
        self.assertEquals(True, "Newsletter present")
        self.assertEquals(True, "Subscription present")
        self.assertEquals(True, "not banned")
        self.assertEquals(True, "not trolled")

        self.assertEquals(p.email_verified)
        self.assertEquals(p.time_zone)
        self.assertEquals(p.marked_troll)
        self.assertEquals(p.marked_troll_at)
        self.assertEquals(p.banned)
        self.assertEquals(p.banned_at)
        self.assertEquals(p.hard_bounced)
        self.assertEquals(p.hard_bounced_at)
        self.assertEquals(p.hard_bounced_message)
        self.assertEquals(p.never_contact_set)
        self.assertEquals(p.never_contact_set_at)
        self.assertEquals(p.personal_contact)
