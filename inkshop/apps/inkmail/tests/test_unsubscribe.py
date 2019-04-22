import logging
import json

from django.urls import reverse
from django.core import mail
from django.conf import settings
from django.test.utils import override_settings

from people.models import Person
from inkmail.models import Subscription, OutgoingMessage
from inkmail.tasks import process_outgoing_message_queue
from utils.factory import Factory
from utils.test_helpers import MockRequestsTestCase, MailTestCase
from utils.encryption import normalize_lower_and_encrypt, normalize_and_encrypt, encrypt, decrypt
import mock
import unittest


class TestUnsubscribeBasics(MailTestCase):

    def setUp(self, *args, **kwargs):
        self.newsletter = Factory.newsletter()
        super(TestUnsubscribeBasics, self).setUp(*args, **kwargs)

    def test_unsubscribe_link_included_in_every_newsletter_message_send(self):
        self.assertEquals(len(mail.outbox), 0)
        self.create_subscribed_person()
        self.send_newsletter_message()

        self.assertEquals(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEquals(OutgoingMessage.objects.count(), 1)
        om = OutgoingMessage.objects.all()[0]
        self.assertIn(om.unsubscribe_link, m.body)

    def test_unsubscribe_link_included_in_every_message_send(self):
        self.assertEquals(len(mail.outbox), 0)
        self.create_subscribed_person()
        self.send_test_message()

        self.assertEquals(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEquals(OutgoingMessage.objects.count(), 1)
        om = OutgoingMessage.objects.all()[0]
        self.assertIn(om.unsubscribe_link, m.body)

    def test_if_unsubscriber_link_is_removed_by_trickery_message_refuses_to_send(self):
        self.assertEquals(len(mail.outbox), 0)
        self.create_subscribed_person()

        Factory.message()
        n = self.newsletter
        n.unsubscribe_footer = ""
        n.save()
        self.send_newsletter_message()
        self.assertEquals(len(mail.outbox), 0)

    def test_unsubscribe_link_is_not_included_in_transactional_messages(self):
        self.assertEquals(len(mail.outbox), 0)
        self.create_subscribed_person()
        self.send_test_transactional_message()

        self.assertEquals(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEquals(OutgoingMessage.objects.count(), 1)
        om = OutgoingMessage.objects.all()[0]
        self.assertNotIn(om.unsubscribe_link, m.body)

    def test_newsletter_footer_included_in_every_message_send(self):
        self.assertEquals(len(mail.outbox), 0)
        self.create_subscribed_person()
        self.send_test_message()

        self.assertEquals(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEquals(OutgoingMessage.objects.count(), 1)
        om = OutgoingMessage.objects.all()[0]
        self.assertIn(om.render_email_string(self.newsletter.unsubscribe_footer), m.body)

    def test_newsletter_footer_included_in_every_newsletter_send(self):
        self.assertEquals(len(mail.outbox), 0)
        self.create_subscribed_person()
        self.send_newsletter_message()

        self.assertEquals(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEquals(OutgoingMessage.objects.count(), 1)
        om = OutgoingMessage.objects.all()[0]
        self.assertIn(om.render_email_string(self.newsletter.unsubscribe_footer), m.body)

    def test_transactional_footer_included_in_every_transactional_send(self):
        self.assertEquals(len(mail.outbox), 0)
        self.create_subscribed_person()
        self.send_test_transactional_message()

        self.assertEquals(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEquals(OutgoingMessage.objects.count(), 1)
        o = Factory.organization()
        om = OutgoingMessage.objects.all()[0]
        self.assertIn(om.render_email_string(o.transactional_footer), m.body)

    def test_transactional_required_fields_included_in_every_transactional_send(self):
        self.assertEquals(len(mail.outbox), 0)
        self.create_subscribed_person()
        self.send_test_transactional_message()

        self.assertEquals(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEquals(OutgoingMessage.objects.count(), 1)
        self.assertIn(self.transactional_message.transactional_send_reason, m.body)
        self.assertIn(self.transactional_message.transactional_no_unsubscribe_reason, m.body)
        om = OutgoingMessage.objects.all()[0]
        self.assertIn(om.delete_account_link, m.body)

    def test_clicking_unsubscribe_marks_unsubscribe(self):
        self.assertEquals(len(mail.outbox), 0)
        self.create_subscribed_person()
        self.assertEquals(self.subscription.unsubscribed, False)
        self.assertEquals(self.subscription.unsubscribed_at, None)
        self.send_newsletter_message()

        self.assertEquals(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEquals(OutgoingMessage.objects.count(), 1)
        om = OutgoingMessage.objects.all()[0]
        self.assertIn(om.unsubscribe_link, m.body)
        self.get(om.unsubscribe_link)
        # Fetch latest
        self.subscription = Subscription.objects.get(pk=self.subscription.pk)
        self.assertEquals(self.subscription.unsubscribed, True)
        self.assertBasicallyEqualTimes(self.subscription.unsubscribed_at, self.now())

    def test_clicking_unsubscribe_prevents_future_mailings(self):
        self.test_clicking_unsubscribe_marks_unsubscribe()
        self.assertEquals(len(mail.outbox), 1)

        self.send_newsletter_message()
        self.assertEquals(len(mail.outbox), 1)


class TestUnsubscribeResubscribe(MailTestCase):

    def setUp(self, *args, **kwargs):
        self.newsletter = Factory.newsletter()
        super(TestUnsubscribeResubscribe, self).setUp(*args, **kwargs)

    def test_unsubscribe_resubscribe_allows_messages_sent(self):
        self.assertEquals(len(mail.outbox), 0)
        self.create_subscribed_person()
        self.assertEquals(self.subscription.unsubscribed, False)
        self.assertEquals(self.subscription.unsubscribed_at, None)
        self.send_newsletter_message()

        self.assertEquals(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEquals(OutgoingMessage.objects.count(), 1)
        om = OutgoingMessage.objects.all()[0]
        self.assertIn(om.unsubscribe_link, m.body)
        self.get(om.unsubscribe_link)
        # Fetch latest
        self.subscription = Subscription.objects.get(pk=self.subscription.pk)
        self.assertEquals(self.subscription.unsubscribed, True)
        self.assertBasicallyEqualTimes(self.subscription.unsubscribed_at, self.now())

        response = self.post(
            reverse(
                'inkmail:subscribe',
            ),
            {
                'first_name': self.person.first_name,
                'email': self.person.email,
                'newsletter': self.newsletter.internal_name,
                'subscription_url': Factory.rand_url(),
            },
        )
        self.assertEquals(response.status_code, 200)

        # Double-opt-in message
        self.assertEquals(len(mail.outbox), 2)

        self.send_newsletter_message()
        self.assertEquals(len(mail.outbox), 3)

    def test_unsubscribe_resubscribe_updates_all_fields(self):
        self.assertEquals(False, "Test written")

    def test_unsubscribe_resubscribe_has_records_of_all_actions(self):
        self.assertEquals(False, "Test written")
