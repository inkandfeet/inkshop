import logging
import json

from utils.helpers import reverse
from django.core import mail
from django.conf import settings
from django.test.utils import override_settings

from people.models import Person
from archives.models import HistoricalEvent
from inkmail.models import Subscription, OutgoingMessage
from inkmail.tasks import process_outgoing_message_queue
from utils.factory import Factory
from utils.test_helpers import MockRequestsTestCase
from utils.encryption import normalize_lower_and_encrypt, normalize_and_encrypt, encrypt, decrypt
import mock
import unittest


class TestPostSubscribes(MockRequestsTestCase):

    def setUp(self, *args, **kwargs):
        self.newsletter = Factory.newsletter()
        super(TestPostSubscribes, self).setUp(*args, **kwargs)

    def test_get_transfer_subscribe_200(self):
        email = Factory.rand_email()
        name = Factory.rand_name()
        response = self.get(
            reverse(
                'inkmail:transfer_subscription', kwargs={"transfer_code": self.newsletter.hashid, },
            ),
            params={
                'f': name,
                'e': email,
                # 'newsletter': self.newsletter.internal_name,
            },
        )

        self.assertEquals(response.status_code, 200)

    def test_get_transfer_subscribe_adds_person_and_subscription(self):
        email = Factory.rand_email()
        name = Factory.rand_name()
        response = self.get(
            reverse(
                'inkmail:transfer_subscription', kwargs={"transfer_code": self.newsletter.hashid, },
            ),
            params={
                'f': name,
                'e': email,
                # 'newsletter': self.newsletter.internal_name,
            },
        )

        self.assertEquals(response.status_code, 200)

        self.assertEquals(Person.objects.count(), 1)
        p = Person.objects.all()[0]
        self.assertEquals(p.first_name, name)
        self.assertEquals(p.email, email)

        self.assertEquals(Subscription.objects.count(), 1)
        s = Subscription.objects.all()[0]
        self.assertEquals(s.person, p)
        self.assertEquals(s.subscription_url, "transfer-subscription")
        self.assertEquals(s.newsletter.name, self.newsletter.name)
        self.assertEquals(s.subscribed_from_ip, self._source_ip)

    def test_no_first_name_subscribe_adds_person_and_subscription(self):
        email = Factory.rand_email()
        response = self.get(
            reverse(
                'inkmail:transfer_subscription', kwargs={"transfer_code": self.newsletter.hashid, },
            ),
            {
                'e': email,
                # 'newsletter': self.newsletter.internal_name,
            },
        )

        self.assertEquals(response.status_code, 200)

        self.assertEquals(Person.objects.count(), 1)
        p = Person.objects.all()[0]
        self.assertEquals(p.email, email)

        self.assertEquals(Subscription.objects.count(), 1)
        s = Subscription.objects.all()[0]
        self.assertEquals(s.person, p)
        self.assertEquals(s.subscription_url, "transfer-subscription")
        self.assertEquals(s.newsletter.name, self.newsletter.name)
        self.assertEquals(s.subscribed_from_ip, self._source_ip)

    def test_newsletter_required(self):
        email = Factory.rand_email()
        name = Factory.rand_name()
        response = self.get(
            reverse(
                'inkmail:transfer_subscription', kwargs={"transfer_code": self.newsletter.hashid, },
            ),
            params={
                'f': name,
                'e': email,
            },
        )

        self.assertEquals(response.status_code, 422)

        self.assertEquals(Person.objects.count(), 0)
        self.assertEquals(Subscription.objects.count(), 0)

    def test_email_required(self):
        name = Factory.rand_name()
        response = self.get(
            reverse(
                'inkmail:transfer_subscription', kwargs={"transfer_code": self.newsletter.hashid, },
            ),
            params={
                'f': name,
                # 'e': email,
                # 'newsletter': self.newsletter.internal_name,
            },
        )

        self.assertEquals(response.status_code, 422)

        self.assertEquals(Person.objects.count(), 0)
        self.assertEquals(Subscription.objects.count(), 0)

        name = Factory.rand_name()
        email = Factory.rand_email()
        response = self.get(
            reverse(
                'inkmail:transfer_subscription', kwargs={"transfer_code": self.newsletter.hashid, },
            ),
            params={
                'f': name,
                'e': email,
                # 'newsletter': self.newsletter.internal_name,
            },
        )

        self.assertEquals(response.status_code, 422)

        self.assertEquals(Person.objects.count(), 0)
        self.assertEquals(Subscription.objects.count(), 0)


class TestWelcomeEmail(MockRequestsTestCase):

    def setUp(self, *args, **kwargs):
        self.newsletter = Factory.newsletter()
        super(TestWelcomeEmail, self).setUp(*args, **kwargs)

    def test_get_transfer_subscribe_200(self):
        email = Factory.rand_email()
        name = Factory.rand_name()
        response = self.get(
            reverse(
                'inkmail:transfer_subscription', kwargs={"transfer_code": self.newsletter.hashid, },
            ),
            params={
                'f': name,
                'e': email,
                # 'newsletter': self.newsletter.internal_name,
            },
        )
        self.assertEquals(response.status_code, 200)
        process_outgoing_message_queue()

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, self.newsletter.welcome_message.subject)
        om = OutgoingMessage.objects.all()[0]
        self.assertIn(
            om.render_email_string(self.newsletter.welcome_message.body_text_unrendered),
            mail.outbox[1].alternatives[0][0]
        )
        self.assertIn(
            om.render_email_string(self.newsletter.welcome_message.body_text_unrendered, plain_text=True),
            mail.outbox[1].body
        )
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(mail.outbox[0].to[0], email)
        self.assertEquals(mail.outbox[0].from_email, self.newsletter.full_from_email)


@override_settings(DISABLE_ENCRYPTION_FOR_TESTS=False)
class TestHistoricalEvent(MockRequestsTestCase):

    def setUp(self, *args, **kwargs):
        self.newsletter = Factory.newsletter()
        super(TestHistoricalEvent, self).setUp(*args, **kwargs)

    def test_get_transfer_subscribe_200(self):
        email = Factory.rand_email()
        name = Factory.rand_name()
        response = self.get(
            reverse(
                'inkmail:transfer_subscription', kwargs={"transfer_code": self.newsletter.hashid, },
            ),
            params={
                'f': name,
                'e': email,
                # 'newsletter': self.newsletter.internal_name,
            },
        )
        self.assertEquals(response.status_code, 200)
        self.assertEquals(HistoricalEvent.objects.count(), 1)
        self.assertEquals(Person.objects.count(), 1)
        self.assertEquals(Subscription.objects.count(), 1)
        he = HistoricalEvent.objects.all()[0]
        p = Person.objects.all()[0]
        s = Subscription.objects.all()[0]
        self.assertEquals(he.event_type, "transfer-subscription")
        self.assertEquals(he.event_creator_type, "person")
        self.assertEquals(he.event_creator_pk, p.pk)
        self.assertHistoricalEventDataEquality(
            he,
            person=p,
            event_type="transfer-subscription",
            newsletter=self.newsletter,
            subscription=s,
        )
