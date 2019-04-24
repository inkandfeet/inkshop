from freezegun import freeze_time
import datetime
import logging
import json
import mock
import unittest

from django.urls import reverse
from django.core import mail
from django.conf import settings
from django.test.utils import override_settings

from people.models import Person
from inkmail.models import Subscription
from inkmail.tasks import process_outgoing_message_queue
from utils.factory import Factory
from utils.test_helpers import MockRequestsTestCase
from utils.encryption import normalize_lower_and_encrypt, normalize_and_encrypt, encrypt, decrypt


class TestDoubleOptIn(MockRequestsTestCase):

    def setUp(self, *args, **kwargs):
        self.newsletter = Factory.newsletter()
        super(TestDoubleOptIn, self).setUp(*args, **kwargs)

    def test_valid_opt_in_click(self):
        self.assertEquals(Subscription.objects.count(), 0)
        email = Factory.rand_email()
        name = Factory.rand_name()
        subscription_url = Factory.rand_url()
        response = self.post(
            reverse(
                'inkmail:subscribe',
            ),
            {
                'first_name': name,
                'email': email,
                'newsletter': self.newsletter.internal_name,
                'subscription_url': subscription_url,
            },
        )
        self.assertEquals(response.status_code, 200)
        process_outgoing_message_queue()

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(Subscription.objects.count(), 1)
        s = Subscription.objects.all()[0]
        self.assertIn(s.opt_in_link, mail.outbox[0].body)

        self.get(s.opt_in_link)
        s = Subscription.objects.get(pk=s.pk)
        self.assertEquals(s.double_opted_in, True)
        self.assertBasicallyEqualTimes(s.double_opted_in_at, self.now())

    def test_invalid_opt_in_click(self):
        self.assertEquals(Subscription.objects.count(), 0)
        email = Factory.rand_email()
        name = Factory.rand_name()
        subscription_url = Factory.rand_url()
        response = self.post(
            reverse(
                'inkmail:subscribe',
            ),
            {
                'first_name': name,
                'email': email,
                'newsletter': self.newsletter.internal_name,
                'subscription_url': subscription_url,
            },
        )
        self.assertEquals(response.status_code, 200)
        process_outgoing_message_queue()

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(Subscription.objects.count(), 1)
        s = Subscription.objects.all()[0]
        self.assertIn(s.opt_in_link, mail.outbox[0].body)

        self.get("%s%s" % (s.opt_in_link, Factory.rand_str(length=2)))
        s = Subscription.objects.get(pk=s.pk)
        self.assertEquals(s.double_opted_in, False)
        self.assertEquals(s.double_opted_in_at, None)

    def test_clicked_confirm_a_second_time(self):
        self.assertEquals(Subscription.objects.count(), 0)
        email = Factory.rand_email()
        name = Factory.rand_name()
        subscription_url = Factory.rand_url()
        response = self.post(
            reverse(
                'inkmail:subscribe',
            ),
            {
                'first_name': name,
                'email': email,
                'newsletter': self.newsletter.internal_name,
                'subscription_url': subscription_url,
            },
        )
        self.assertEquals(response.status_code, 200)
        process_outgoing_message_queue()

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(Subscription.objects.count(), 1)
        s = Subscription.objects.all()[0]
        self.assertIn(s.opt_in_link, mail.outbox[0].body)

        self.get(s.opt_in_link)
        s = Subscription.objects.get(pk=s.pk)
        self.assertEquals(s.double_opted_in, True)
        self.assertBasicallyEqualTimes(s.double_opted_in_at, self.now())
        first_time = s.double_opted_in_at

        # Click it again
        self.get(s.opt_in_link)
        s = Subscription.objects.get(pk=s.pk)
        self.assertEquals(s.double_opted_in, True)
        self.assertBasicallyEqualTimes(s.double_opted_in_at, first_time)

    def test_clicked_confirm_over_a_week_later(self):
        self.assertEquals(Subscription.objects.count(), 0)
        email = Factory.rand_email()
        name = Factory.rand_name()
        subscription_url = Factory.rand_url()
        response = self.post(
            reverse(
                'inkmail:subscribe',
            ),
            {
                'first_name': name,
                'email': email,
                'newsletter': self.newsletter.internal_name,
                'subscription_url': subscription_url,
            },
        )
        self.assertEquals(response.status_code, 200)
        process_outgoing_message_queue()

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(Subscription.objects.count(), 1)
        s = Subscription.objects.all()[0]
        self.assertIn(s.opt_in_link, mail.outbox[0].body)

        self.get(s.opt_in_link)
        s = Subscription.objects.get(pk=s.pk)
        self.assertEquals(s.double_opted_in, True)
        self.assertBasicallyEqualTimes(s.double_opted_in_at, self.now())
        first_time = s.double_opted_in_at

        # Click it again
        with freeze_time(self.now() + datetime.timedelta(days=7)):
            self.get(s.opt_in_link)
            s = Subscription.objects.get(pk=s.pk)
            self.assertEquals(s.double_opted_in, True)
            self.assertBasicallyEqualTimes(s.double_opted_in_at, first_time)
