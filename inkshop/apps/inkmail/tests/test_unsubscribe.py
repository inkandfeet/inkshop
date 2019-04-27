import logging
import json
from utils.helpers import reverse
from django.core import mail
from django.conf import settings

from django.test.utils import override_settings

from archives.models import HistoricalEvent
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
        self.assertIn(om.render_email_string(self.newsletter.unsubscribe_footer, plain_text=True), m.body)

    def test_newsletter_footer_included_in_every_newsletter_send(self):
        self.assertEquals(len(mail.outbox), 0)
        self.create_subscribed_person()
        self.send_newsletter_message()

        self.assertEquals(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEquals(OutgoingMessage.objects.count(), 1)
        om = OutgoingMessage.objects.all()[0]
        self.assertIn(om.render_email_string(self.newsletter.unsubscribe_footer, plain_text=True), m.body)

    def test_transactional_footer_included_in_every_transactional_send(self):
        self.assertEquals(len(mail.outbox), 0)
        self.create_subscribed_person()
        self.send_test_transactional_message()

        self.assertEquals(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEquals(OutgoingMessage.objects.count(), 1)
        o = Factory.organization()
        om = OutgoingMessage.objects.all()[0]
        self.assertIn(om.render_email_string(o.transactional_footer, plain_text=True), m.body)

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


@override_settings(DISABLE_ENCRYPTION_FOR_TESTS=False)
class TestUnsubscribeResubscribe(MailTestCase):

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

        # Unsubscribe
        self.assertIn(om.unsubscribe_link, m.body)
        self.get(om.unsubscribe_link)

        # Fetch updated subscription
        self.subscription = Subscription.objects.get(pk=self.subscription.pk)
        self.assertEquals(self.subscription.unsubscribed, True)
        self.assertEquals(self.subscription.double_opted_in, False)
        self.assertEquals(self.subscription.double_opted_in_at, None)
        self.assertBasicallyEqualTimes(self.subscription.unsubscribed_at, self.now())

        # Re-subscribe
        response = self.post(
            "%s%s" % (
                settings.MAIL_BASE_URL,
                reverse(
                    'inkmail:subscribe',
                    host='mail',
                )
            ),
            {
                'first_name': self.person.first_name,
                'email': self.person.email,
                'newsletter': self.newsletter.internal_name,
                'subscription_url': Factory.rand_url(),
            },
        )
        self.assertEquals(response.status_code, 200)
        self.subscription = Subscription.objects.get(pk=self.subscription.pk)
        self.assertEquals(self.subscription.unsubscribed, False)
        self.assertEquals(self.subscription.unsubscribed_at, None)

        process_outgoing_message_queue()

        self.assertEquals(len(mail.outbox), 2)
        self.assertEquals(Subscription.objects.count(), 1)
        s = Subscription.objects.all()[0]
        self.assertIn(s.opt_in_link, mail.outbox[1].body)

        # Re-double-opt-in
        self.get(self.subscription.opt_in_link)

        self.subscription = Subscription.objects.get(pk=self.subscription.pk)
        self.assertEquals(self.subscription.unsubscribed, False)
        self.assertEquals(self.subscription.unsubscribed_at, None)
        self.assertEquals(self.subscription.double_opted_in, True)
        self.assertBasicallyEqualTimes(self.subscription.double_opted_in_at, self.now())

        process_outgoing_message_queue()

        # Welcome email re-sent
        self.assertEquals(len(mail.outbox), 3)

        # Send newsletter, make sure it sent.
        self.send_newsletter_message()
        process_outgoing_message_queue()
        self.assertEquals(len(mail.outbox), 4)

    def test_unsubscribe_resubscribe_updates_all_fields(self):
        self.assertEquals(len(mail.outbox), 0)
        self.create_subscribed_person()
        self.assertEquals(self.subscription.unsubscribed, False)
        self.assertEquals(self.subscription.unsubscribed_at, None)
        self.send_newsletter_message()

        self.assertEquals(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEquals(OutgoingMessage.objects.count(), 1)
        om = OutgoingMessage.objects.all()[0]

        # Unsubscribe
        self.assertIn(om.unsubscribe_link, m.body)
        self.get(om.unsubscribe_link)

        # Fetch updated subscription
        self.subscription = Subscription.objects.get(pk=self.subscription.pk)
        self.assertEquals(self.subscription.unsubscribed, True)
        self.assertBasicallyEqualTimes(self.subscription.unsubscribed_at, self.now())

        # Re-subscribe
        name = Factory.rand_name()
        subscription_url = Factory.rand_url()

        response = self.post(
            "%s%s" % (
                settings.MAIL_BASE_URL,
                reverse(
                    'inkmail:subscribe',
                    host='mail',
                )
            ),
            {
                'first_name': name,
                'email': self.person.email,
                'newsletter': self.newsletter.internal_name,
                'subscription_url': subscription_url,
            },
        )
        self.assertEquals(response.status_code, 200)
        self.assertEquals(Subscription.objects.count(), 1)
        self.subscription = Subscription.objects.get(pk=self.subscription.pk)
        self.assertEquals(self.subscription.unsubscribed, False)
        self.assertEquals(self.subscription.unsubscribed_at, None)

        process_outgoing_message_queue()
        self.assertEquals(len(mail.outbox), 2)
        self.assertEquals(Subscription.objects.count(), 1)
        s = Subscription.objects.all()[0]
        self.assertIn(s.opt_in_link, mail.outbox[1].body)

        # Re-double-opt-in
        self.get(s.opt_in_link)
        self.subscription = Subscription.objects.get(pk=self.subscription.pk)
        self.assertEquals(self.subscription.unsubscribed, False)
        self.assertEquals(self.subscription.unsubscribed_at, None)
        process_outgoing_message_queue()

        # Check fields
        self.person = Person.objects.get(pk=self.person.pk)
        self.assertEquals(self.person.first_name, name)
        self.assertEquals(self.subscription.subscription_url, subscription_url)

    def test_unsubscribe_resubscribe_has_records_of_all_actions(self):
        self.newsletter = Factory.newsletter()
        self.assertEquals(HistoricalEvent.objects.count(), 0)
        email = Factory.rand_email()
        name = Factory.rand_name()
        subscription_url = Factory.rand_url()
        response = self.post(
            "%s%s" % (
                settings.MAIL_BASE_URL,
                reverse(
                    'inkmail:subscribe',
                    host='mail',
                )
            ),
            {
                'first_name': name,
                'email': email,
                'newsletter': self.newsletter.internal_name,
                'subscription_url': subscription_url,
            },
        )

        self.assertEquals(response.status_code, 200)

        self.assertEquals(Person.objects.count(), 1)
        self.assertEquals(Subscription.objects.count(), 1)
        p = Person.objects.all()[0]
        s = Subscription.objects.all()[0]

        self.assertEquals(HistoricalEvent.objects.count(), 1)
        he = HistoricalEvent.objects.order_by("-created_at").all()[0]
        self.assertEquals(he.event_type, "subscribed")
        self.assertEquals(he.event_creator_type, "person")
        self.assertEquals(he.event_creator_pk, p.pk)
        self.assertHistoricalEventDataEquality(
            he,
            person=p,
            event_type="subscribed",
            newsletter=self.newsletter,
            subscription=s,
        )

        # Unsubscribe
        om = OutgoingMessage.objects.all()[0]
        self.get(om.unsubscribe_link)

        s = Subscription.objects.get(pk=s.pk)
        self.assertEquals(HistoricalEvent.objects.count(), 2)
        he = HistoricalEvent.objects.order_by("-created_at").all()[0]
        self.assertEquals(he.event_type, "unsubscribe")
        self.assertEquals(he.event_creator_type, "person")
        self.assertEquals(he.event_creator_pk, p.pk)
        self.assertHistoricalEventDataEquality(
            he,
            person=p,
            event_type="unsubscribe",
            subscription=s,
            outgoingmessage=om,
        )

        # Fetch updated subscription
        s = Subscription.objects.get(pk=s.pk)

        # Re-subscribe
        name = Factory.rand_name()
        subscription_url = Factory.rand_url()
        response = self.post(
            "%s%s" % (
                settings.MAIL_BASE_URL,
                reverse(
                    'inkmail:subscribe',
                    host='mail',
                )
            ),
            {
                'first_name': name,
                'email': p.email,
                'newsletter': self.newsletter.internal_name,
                'subscription_url': subscription_url,
            },
        )
        self.assertEquals(response.status_code, 200)
        s = Subscription.objects.get(pk=s.pk)
        p = Person.objects.get(pk=p.pk)

        self.assertEquals(HistoricalEvent.objects.count(), 3)
        he = HistoricalEvent.objects.order_by("-created_at").all()[0]
        self.assertEquals(he.event_type, "subscribed")
        self.assertEquals(he.event_creator_type, "person")
        self.assertEquals(he.event_creator_pk, p.pk)
        self.assertHistoricalEventDataEquality(
            he,
            person=p,
            event_type="subscribed",
            newsletter=self.newsletter,
            subscription=s,
        )

        process_outgoing_message_queue()

        # Re-double-opt-in
        self.get(s.opt_in_link)

        s = Subscription.objects.get(pk=s.pk)
        p = Person.objects.get(pk=p.pk)

        self.assertEquals(HistoricalEvent.objects.count(), 4)
        he = HistoricalEvent.objects.order_by("-created_at").all()[0]
        self.assertEquals(he.event_type, "double-opt-in")
        self.assertEquals(he.event_creator_type, "person")
        self.assertEquals(he.event_creator_pk, p.pk)
        self.assertHistoricalEventDataEquality(
            he,
            person=p,
            event_type="double-opt-in",
            newsletter=self.newsletter,
            subscription=s,
        )
