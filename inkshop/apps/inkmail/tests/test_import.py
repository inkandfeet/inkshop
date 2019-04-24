import logging
import json
import mock
import unittest

from django.urls import reverse
from django.core import mail
from django.conf import settings
from django.test.utils import override_settings
from django.utils import timezone
from freezegun import freeze_time

from people.models import Person
from inkmail.models import Subscription, Newsletter
from utils.factory import Factory
from utils.test_helpers import MailTestCase
from utils.encryption import normalize_lower_and_encrypt, normalize_and_encrypt, encrypt, decrypt
from utils.encryption import lookup_hash


class TestNewsletterImport(MailTestCase):

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
        self.assertEquals(Person.objects.count(), 0)
        self.assertEquals(Subscription.objects.count(), 0)

        import_source = Factory.rand_str()
        email = Factory.rand_email()
        subscribed_at = Factory.rand_datetime()
        subscription_url = Factory.rand_url()
        double_opted_in = Factory.rand_bool()
        double_opted_in_at = Factory.rand_datetime()
        first_name = Factory.rand_name()
        last_name = Factory.rand_name()
        subscription_ip = Factory.rand_ip()
        time_zone = Factory.rand_timezone()
        import_time = timezone.now()

        self.newsletter.import_subscriber(
            import_source=import_source,
            email=email,
            subscribed_at=subscribed_at,
            subscription_url=subscription_url,
            double_opted_in=double_opted_in,
            double_opted_in_at=double_opted_in_at,
            first_name=first_name,
            last_name=last_name,
            subscription_ip=subscription_ip,
            time_zone=time_zone,
            newsletter_name=self.newsletter.internal_name,
        )

        self.assertEquals(Person.objects.count(), 1)
        self.assertEquals(Newsletter.objects.count(), 1)
        self.assertEquals(Subscription.objects.count(), 1)
        p = Person.objects.all()[0]
        s = Subscription.objects.all()[0]

        # Check person
        self.assertEquals(p.first_name, first_name)
        self.assertEquals(p.last_name, last_name)
        self.assertEquals(p.email, email)
        self.assertEquals(p.hashed_first_name, lookup_hash(first_name))
        self.assertEquals(p.hashed_last_name, lookup_hash(last_name))
        self.assertEquals(p.hashed_email, lookup_hash(email))
        self.assertEquals(p.email_verified, double_opted_in)
        self.assertEquals(p.time_zone, time_zone)
        self.assertEquals(p.was_imported, True)
        self.assertBasicallyEqualTimes(p.was_imported_at, import_time)
        self.assertEquals(p.import_source, import_source)
        self.assertEquals(p.marked_troll, False)
        self.assertEquals(p.marked_troll_at, None)
        self.assertEquals(p.banned, False)
        self.assertEquals(p.banned_at, None)
        self.assertEquals(p.hard_bounced, False)
        self.assertEquals(p.hard_bounced_at, None)
        self.assertEquals(p.hard_bounced_reason, None)
        self.assertEquals(p.hard_bounced_message, None)
        self.assertEquals(p.never_contact_set, False)
        self.assertEquals(p.never_contact_set_at, None)
        self.assertEquals(p.personal_contact, False)

        # Check subscription
        self.assertEquals(s.person, p)
        self.assertEquals(s.newsletter, self.newsletter)
        self.assertBasicallyEqualTimes(s.subscribed_at, import_time)
        self.assertEquals(s.subscription_url, subscription_url)
        self.assertEquals(s.subscribed_from_ip, subscription_ip)
        self.assertEquals(s.was_imported, True)
        self.assertBasicallyEqualTimes(s.was_imported_at, import_time)
        self.assertEquals(s.import_source, import_source)
        self.assertEquals(s.double_opted_in, double_opted_in)
        self.assertBasicallyEqualTimes(s.double_opted_in_at, double_opted_in_at)
        self.assertEquals(s.has_set_never_unsubscribe, False)
        self.assertEquals(s.unsubscribed, False)
        self.assertEquals(s.unsubscribed_at, None)

    def test_import_with_minimum_fields_works(self):
        s = None
        p = None
        self.assertEquals(Person.objects.count(), 0)
        self.assertEquals(Subscription.objects.count(), 0)

        import_source = Factory.rand_str()
        email = Factory.rand_email()
        subscribed_at = Factory.rand_datetime()
        subscription_url = Factory.rand_url()
        double_opted_in = Factory.rand_bool()
        import_time = timezone.now()

        self.newsletter.import_subscriber(
            import_source=import_source,
            email=email,
            subscribed_at=subscribed_at,
            subscription_url=subscription_url,
            double_opted_in=double_opted_in,
            newsletter_name=self.newsletter.internal_name,
        )

        self.assertEquals(Person.objects.count(), 1)
        self.assertEquals(Newsletter.objects.count(), 1)
        self.assertEquals(Subscription.objects.count(), 1)
        p = Person.objects.all()[0]
        s = Subscription.objects.all()[0]

        # Check person
        self.assertEquals(p.first_name, None)
        self.assertEquals(p.last_name, None)
        self.assertEquals(p.email, email)
        self.assertEquals(p.hashed_first_name, lookup_hash(None))
        self.assertEquals(p.hashed_last_name, lookup_hash(None))
        self.assertEquals(p.hashed_email, lookup_hash(email))
        self.assertEquals(p.email_verified, double_opted_in)
        self.assertEquals(p.time_zone, None)
        self.assertEquals(p.was_imported, True)
        self.assertBasicallyEqualTimes(p.was_imported_at, import_time)
        self.assertEquals(p.import_source, import_source)
        self.assertEquals(p.marked_troll, False)
        self.assertEquals(p.marked_troll_at, None)
        self.assertEquals(p.banned, False)
        self.assertEquals(p.banned_at, None)
        self.assertEquals(p.hard_bounced, False)
        self.assertEquals(p.hard_bounced_at, None)
        self.assertEquals(p.hard_bounced_reason, None)
        self.assertEquals(p.hard_bounced_message, None)
        self.assertEquals(p.never_contact_set, False)
        self.assertEquals(p.never_contact_set_at, None)
        self.assertEquals(p.personal_contact, False)

        # Check subscription
        self.assertEquals(s.person, p)
        self.assertEquals(s.newsletter, self.newsletter)
        self.assertBasicallyEqualTimes(s.subscribed_at, import_time)
        self.assertEquals(s.subscription_url, subscription_url)
        self.assertEquals(s.subscribed_from_ip, None)
        self.assertEquals(s.was_imported, True)
        self.assertBasicallyEqualTimes(s.was_imported_at, import_time)
        self.assertEquals(s.import_source, import_source)
        self.assertEquals(s.double_opted_in, double_opted_in)
        self.assertEquals(s.double_opted_in_at, None)
        self.assertEquals(s.has_set_never_unsubscribe, False)
        self.assertEquals(s.unsubscribed, False)
        self.assertEquals(s.unsubscribed_at, None)

    def test_import_with_no_newsletter_creates_person_but_not_subscription(self):
        self.assertEquals(Person.objects.count(), 0)
        self.assertEquals(Subscription.objects.count(), 0)

        import_source = Factory.rand_str()
        email = Factory.rand_email()
        subscribed_at = Factory.rand_datetime()
        subscription_url = Factory.rand_url()
        double_opted_in = Factory.rand_bool()

        self.newsletter.import_subscriber(
            import_source=import_source,
            email=email,
            subscribed_at=subscribed_at,
            subscription_url=subscription_url,
            double_opted_in=double_opted_in,
        )

        self.assertEquals(Person.objects.count(), 1)
        self.assertEquals(Newsletter.objects.count(), 1)
        self.assertEquals(Subscription.objects.count(), 0)

    def test_import_does_not_overwrite_by_default(self):
        s = None
        p = None
        self.assertEquals(Person.objects.count(), 0)
        self.assertEquals(Subscription.objects.count(), 0)

        first_import_source = Factory.rand_str()
        email = Factory.rand_email()
        first_subscribed_at = Factory.rand_datetime()
        first_subscription_url = Factory.rand_url()
        first_double_opted_in = Factory.rand_bool()
        first_double_opted_in_at = Factory.rand_datetime()
        first_first_name = Factory.rand_name()
        first_last_name = Factory.rand_name()
        first_subscription_ip = Factory.rand_ip()
        first_time_zone = Factory.rand_timezone()
        first_import_time = timezone.now()

        self.newsletter.import_subscriber(
            import_source=first_import_source,
            email=email,
            subscribed_at=first_subscribed_at,
            subscription_url=first_subscription_url,
            double_opted_in=first_double_opted_in,
            double_opted_in_at=first_double_opted_in_at,
            first_name=first_first_name,
            last_name=first_last_name,
            subscription_ip=first_subscription_ip,
            time_zone=first_time_zone,
            newsletter_name=self.newsletter.internal_name,
        )

        second_import_source = Factory.rand_str()
        second_subscribed_at = Factory.rand_datetime()
        second_subscription_url = Factory.rand_url()
        second_double_opted_in = Factory.rand_bool()
        second_double_opted_in_at = Factory.rand_datetime()
        second_second_name = Factory.rand_name()
        second_last_name = Factory.rand_name()
        second_subscription_ip = Factory.rand_ip()
        second_time_zone = Factory.rand_timezone()
        second_import_time = timezone.now()  # noqa

        self.newsletter.import_subscriber(
            import_source=second_import_source,
            email=email,
            subscribed_at=second_subscribed_at,
            subscription_url=second_subscription_url,
            double_opted_in=second_double_opted_in,
            double_opted_in_at=second_double_opted_in_at,
            first_name=second_second_name,
            last_name=second_last_name,
            subscription_ip=second_subscription_ip,
            time_zone=second_time_zone,
            newsletter_name=self.newsletter.internal_name,
        )

        self.assertEquals(Person.objects.count(), 1)
        self.assertEquals(Newsletter.objects.count(), 1)
        self.assertEquals(Subscription.objects.count(), 1)
        p = Person.objects.all()[0]
        s = Subscription.objects.all()[0]

        # Check person
        self.assertEquals(p.first_name, first_first_name)
        self.assertEquals(p.last_name, first_last_name)
        self.assertEquals(p.email, email)
        self.assertEquals(p.hashed_first_name, lookup_hash(first_first_name))
        self.assertEquals(p.hashed_last_name, lookup_hash(first_last_name))
        self.assertEquals(p.hashed_email, lookup_hash(email))
        self.assertEquals(p.email_verified, first_double_opted_in)
        self.assertEquals(p.time_zone, first_time_zone)
        self.assertEquals(p.was_imported, True)
        self.assertBasicallyEqualTimes(p.was_imported_at, first_import_time)
        self.assertEquals(p.import_source, first_import_source)
        self.assertEquals(p.marked_troll, False)
        self.assertEquals(p.marked_troll_at, None)
        self.assertEquals(p.banned, False)
        self.assertEquals(p.banned_at, None)
        self.assertEquals(p.hard_bounced, False)
        self.assertEquals(p.hard_bounced_at, None)
        self.assertEquals(p.hard_bounced_reason, None)
        self.assertEquals(p.hard_bounced_message, None)
        self.assertEquals(p.never_contact_set, False)
        self.assertEquals(p.never_contact_set_at, None)
        self.assertEquals(p.personal_contact, False)

        # Check subscription
        self.assertEquals(s.person, p)
        self.assertEquals(s.newsletter, self.newsletter)
        self.assertBasicallyEqualTimes(s.subscribed_at, first_import_time)
        self.assertEquals(s.subscription_url, first_subscription_url)
        self.assertEquals(s.subscribed_from_ip, first_subscription_ip)
        self.assertEquals(s.was_imported, True)
        self.assertBasicallyEqualTimes(s.was_imported_at, first_import_time)
        self.assertEquals(s.import_source, first_import_source)
        self.assertEquals(s.double_opted_in, first_double_opted_in)
        self.assertBasicallyEqualTimes(s.double_opted_in_at, first_double_opted_in_at)
        self.assertEquals(s.has_set_never_unsubscribe, False)
        self.assertEquals(s.unsubscribed, False)
        self.assertEquals(s.unsubscribed_at, None)

    def test_import_overwrites_if_told_to(self):
        s = None
        p = None
        self.assertEquals(Person.objects.count(), 0)
        self.assertEquals(Subscription.objects.count(), 0)

        first_import_source = Factory.rand_str()
        email = Factory.rand_email()
        first_subscribed_at = Factory.rand_datetime()
        first_subscription_url = Factory.rand_url()
        first_double_opted_in = Factory.rand_bool()
        first_double_opted_in_at = Factory.rand_datetime()
        first_first_name = Factory.rand_name()
        first_last_name = Factory.rand_name()
        first_subscription_ip = Factory.rand_ip()
        first_time_zone = Factory.rand_timezone()

        self.newsletter.import_subscriber(
            import_source=first_import_source,
            email=email,
            subscribed_at=first_subscribed_at,
            subscription_url=first_subscription_url,
            double_opted_in=first_double_opted_in,
            double_opted_in_at=first_double_opted_in_at,
            first_name=first_first_name,
            last_name=first_last_name,
            subscription_ip=first_subscription_ip,
            time_zone=first_time_zone,
            newsletter_name=self.newsletter.internal_name,
        )

        second_import_source = Factory.rand_str()
        second_subscribed_at = Factory.rand_datetime()
        second_subscription_url = Factory.rand_url()
        second_double_opted_in = Factory.rand_bool()
        second_double_opted_in_at = Factory.rand_datetime()
        second_second_name = Factory.rand_name()
        second_last_name = Factory.rand_name()
        second_subscription_ip = Factory.rand_ip()
        second_time_zone = Factory.rand_timezone()
        second_import_time = timezone.now()  # noqa

        self.newsletter.import_subscriber(
            import_source=second_import_source,
            email=email,
            subscribed_at=second_subscribed_at,
            subscription_url=second_subscription_url,
            double_opted_in=second_double_opted_in,
            double_opted_in_at=second_double_opted_in_at,
            first_name=second_second_name,
            last_name=second_last_name,
            subscription_ip=second_subscription_ip,
            time_zone=second_time_zone,
            newsletter_name=self.newsletter.internal_name,
            overwrite=True,
        )

        self.assertEquals(Person.objects.count(), 1)
        self.assertEquals(Newsletter.objects.count(), 1)
        self.assertEquals(Subscription.objects.count(), 1)
        p = Person.objects.all()[0]
        s = Subscription.objects.all()[0]

        # Check person
        self.assertEquals(p.first_name, second_second_name)
        self.assertEquals(p.last_name, second_last_name)
        self.assertEquals(p.email, email)
        self.assertEquals(p.hashed_first_name, lookup_hash(second_second_name))
        self.assertEquals(p.hashed_last_name, lookup_hash(second_last_name))
        self.assertEquals(p.hashed_email, lookup_hash(email))
        self.assertEquals(p.email_verified, second_double_opted_in)
        self.assertEquals(p.time_zone, second_time_zone)
        self.assertEquals(p.was_imported, True)
        self.assertBasicallyEqualTimes(p.was_imported_at, second_import_time)
        self.assertEquals(p.import_source, second_import_source)
        self.assertEquals(p.marked_troll, False)
        self.assertEquals(p.marked_troll_at, None)
        self.assertEquals(p.banned, False)
        self.assertEquals(p.banned_at, None)
        self.assertEquals(p.hard_bounced, False)
        self.assertEquals(p.hard_bounced_at, None)
        self.assertEquals(p.hard_bounced_reason, None)
        self.assertEquals(p.hard_bounced_message, None)
        self.assertEquals(p.never_contact_set, False)
        self.assertEquals(p.never_contact_set_at, None)
        self.assertEquals(p.personal_contact, False)

        # Check subscription
        self.assertEquals(s.person, p)
        self.assertEquals(s.newsletter, self.newsletter)
        self.assertBasicallyEqualTimes(s.subscribed_at, second_import_time)
        self.assertEquals(s.subscription_url, second_subscription_url)
        self.assertEquals(s.subscribed_from_ip, second_subscription_ip)
        self.assertEquals(s.was_imported, True)
        self.assertBasicallyEqualTimes(s.was_imported_at, second_import_time)
        self.assertEquals(s.import_source, second_import_source)
        self.assertEquals(s.double_opted_in, second_double_opted_in)
        self.assertBasicallyEqualTimes(s.double_opted_in_at, second_double_opted_in_at)
        self.assertEquals(s.has_set_never_unsubscribe, False)
        self.assertEquals(s.unsubscribed, False)
        self.assertEquals(s.unsubscribed_at, None)

    @unittest.skip("TODO: Decide how to handle import flow for people who don't have double-opt-in records.")
    def test_import_gets_confirmation_if_people_are_not_double_opted_in(self):
        # TODO: Decide how to handle import flow for people who don't have double-opt-in records.
        self.assertEquals(False, "Test written")

    def test_import_ignores_banned_people(self):
        self.assertEquals(Person.objects.count(), 0)
        self.assertEquals(Subscription.objects.count(), 0)

        banned_person = Factory.person()
        banned_person.ban()
        self.assertEquals(Person.objects.count(), 1)
        self.assertEquals(Subscription.objects.count(), 0)

        import_source = Factory.rand_str()
        email = banned_person.email
        subscribed_at = Factory.rand_datetime()
        subscription_url = Factory.rand_url()
        double_opted_in = Factory.rand_bool()

        self.newsletter.import_subscriber(
            import_source=import_source,
            email=email,
            subscribed_at=subscribed_at,
            subscription_url=subscription_url,
            double_opted_in=double_opted_in,
            newsletter_name=self.newsletter.internal_name,
            overwrite=True,
        )

        self.assertEquals(Person.objects.count(), 1)
        self.assertEquals(Newsletter.objects.count(), 1)
        self.assertEquals(Subscription.objects.count(), 0)

    def test_import_imports_trolls_but_marks_them(self):
        self.assertEquals(Person.objects.count(), 0)
        self.assertEquals(Subscription.objects.count(), 0)

        troll = Factory.person()
        troll.mark_troll()
        self.assertEquals(Person.objects.count(), 1)

        import_source = Factory.rand_str()
        email = troll.email
        subscribed_at = Factory.rand_datetime()
        subscription_url = Factory.rand_url()
        double_opted_in = Factory.rand_bool()
        import_time = timezone.now()

        self.newsletter.import_subscriber(
            import_source=import_source,
            email=email,
            subscribed_at=subscribed_at,
            subscription_url=subscription_url,
            double_opted_in=double_opted_in,
            newsletter_name=self.newsletter.internal_name,
            overwrite=True,
        )

        self.assertEquals(Person.objects.count(), 1)
        self.assertEquals(Newsletter.objects.count(), 1)
        self.assertEquals(Subscription.objects.count(), 1)
        p = Person.objects.all()[0]
        s = Subscription.objects.all()[0]

        # Check person
        self.assertEquals(p.first_name, None)
        self.assertEquals(p.last_name, None)
        self.assertEquals(p.email, email)
        self.assertEquals(p.hashed_first_name, lookup_hash(None))
        self.assertEquals(p.hashed_last_name, lookup_hash(None))
        self.assertEquals(p.hashed_email, lookup_hash(email))
        self.assertEquals(p.email_verified, double_opted_in)
        self.assertEquals(p.time_zone, None)
        self.assertEquals(p.was_imported, True)
        self.assertBasicallyEqualTimes(p.was_imported_at, import_time)
        self.assertEquals(p.import_source, import_source)
        self.assertEquals(p.marked_troll, True)
        self.assertBasicallyEqualTimes(p.marked_troll_at, import_time)
        self.assertEquals(p.banned, False)
        self.assertEquals(p.banned_at, None)
        self.assertEquals(p.hard_bounced, False)
        self.assertEquals(p.hard_bounced_at, None)
        self.assertEquals(p.hard_bounced_reason, None)
        self.assertEquals(p.hard_bounced_message, None)
        self.assertEquals(p.never_contact_set, False)
        self.assertEquals(p.never_contact_set_at, None)
        self.assertEquals(p.personal_contact, False)

        # Check subscription
        self.assertEquals(s.person, p)
        self.assertEquals(s.newsletter, self.newsletter)
        self.assertBasicallyEqualTimes(s.subscribed_at, import_time)
        self.assertEquals(s.subscription_url, subscription_url)
        self.assertEquals(s.subscribed_from_ip, None)
        self.assertEquals(s.was_imported, True)
        self.assertBasicallyEqualTimes(s.was_imported_at, import_time)
        self.assertEquals(s.import_source, import_source)
        self.assertEquals(s.double_opted_in, double_opted_in)
        self.assertEquals(s.double_opted_in_at, None)
        self.assertEquals(s.has_set_never_unsubscribe, False)
        self.assertEquals(s.unsubscribed, False)
        self.assertEquals(s.unsubscribed_at, None)


# TODO: Enable when purchases are added.
@unittest.skip("Once purchases are added in.")
class TestPurchaserImport(MailTestCase):

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
