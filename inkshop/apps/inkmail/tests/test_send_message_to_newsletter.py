import datetime
import logging
import json
from freezegun import freeze_time

from utils.helpers import reverse
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

from inkmail.tasks import process_outgoing_message_queue
from inkmail.helpers import queue_message, queue_newsletter_message, queue_transactional_message


class TestSendToNewsletter(MailTestCase):

    def setUp(self, *args, **kwargs):
        # Create 3 newsletters
        self.newsletter = Factory.newsletter()
        # Create 5-10 subscribers for each

        # Create 5-15 people not subscribed to either

        super(TestSendToNewsletter, self).setUp(*args, **kwargs)

    def test_sends_to_everyone_in_list(self):
        people = []
        num_subscribers = Factory.rand_int(end=20)
        for i in range(0, num_subscribers):
            s = Factory.subscription(newsletter=self.newsletter)
            s.double_opt_in()
            people.append(s)

        self.send_newsletter_message()
        self.assertEquals(len(mail.outbox), num_subscribers)

    def test_does_not_send_to_everyone_not_in_list(self):
        subscribed_people = []
        subscribed_people_emails = []
        nonsubscribed_people = []
        nonsubscribed_people_emails = []
        num_subscribers = Factory.rand_int(end=20)
        num_nonsubscribers = Factory.rand_int(end=20)
        for i in range(0, num_subscribers):
            s = Factory.subscription(newsletter=self.newsletter)
            s.double_opt_in()
            subscribed_people.append(s)
            subscribed_people_emails.append(s.person.email)

        for i in range(0, num_nonsubscribers):
            p = Factory.person()
            nonsubscribed_people.append(p)
            nonsubscribed_people_emails.append(p.email)

        self.send_newsletter_message()
        self.assertEquals(len(mail.outbox), num_subscribers)
        for m in mail.outbox:
            self.assertEquals(len(m.to), 1)
            self.assertIn(m.to[0], subscribed_people_emails)
            self.assertNotIn(m.to[0], nonsubscribed_people_emails)

    def test_if_called_multiple_times_only_sends_once(self):
        people = []
        num_subscribers = Factory.rand_int(end=20)
        for i in range(0, num_subscribers):
            s = Factory.subscription(newsletter=self.newsletter)
            s.double_opt_in()
            people.append(s)

        self.scheduled_newsletter_message = Factory.scheduled_newsletter_message(
            newsletter=self.newsletter,
            send_at_date=self.now(),
            send_at_hour=self.now().hour,
            send_at_minute=self.now().minute,
            use_local_time=False,
        )
        self.subject = self.scheduled_newsletter_message.message.subject
        self.body = self.scheduled_newsletter_message.message.body_text_unrendered
        queue_newsletter_message(self.scheduled_newsletter_message.hashid)
        process_outgoing_message_queue()
        process_outgoing_message_queue()
        process_outgoing_message_queue()
        process_outgoing_message_queue()
        self.assertEquals(len(mail.outbox), num_subscribers)

    def test_if_scheduled_for_future_does_not_send_until_future(self):
        people = []
        num_subscribers = Factory.rand_int(end=20)
        for i in range(0, num_subscribers):
            s = Factory.subscription(newsletter=self.newsletter)
            s.double_opt_in()
            people.append(s)

        future_date = self.now() + datetime.timedelta(hours=1)
        self.scheduled_newsletter_message = Factory.scheduled_newsletter_message(
            newsletter=self.newsletter,
            send_at_date=future_date,
            send_at_hour=future_date.hour,
            send_at_minute=future_date.minute,
            use_local_time=False,
        )
        self.subject = self.scheduled_newsletter_message.message.subject
        self.body = self.scheduled_newsletter_message.message.body_text_unrendered
        queue_newsletter_message(self.scheduled_newsletter_message.hashid)
        process_outgoing_message_queue()
        self.assertEquals(len(mail.outbox), 0)

        with freeze_time(self.now() + datetime.timedelta(hours=1)):
            process_outgoing_message_queue()
            self.assertEquals(len(mail.outbox), num_subscribers)

    def test_if_scheduled_for_past_time_sends_immediately(self):
        people = []
        num_subscribers = Factory.rand_int(end=20)
        for i in range(0, num_subscribers):
            s = Factory.subscription(newsletter=self.newsletter)
            s.double_opt_in()
            people.append(s)

        future_date = self.now() - datetime.timedelta(hours=1)
        self.scheduled_newsletter_message = Factory.scheduled_newsletter_message(
            newsletter=self.newsletter,
            send_at_date=future_date,
            send_at_hour=future_date.hour,
            send_at_minute=future_date.minute,
            use_local_time=False,
        )
        self.subject = self.scheduled_newsletter_message.message.subject
        self.body = self.scheduled_newsletter_message.message.body_text_unrendered
        queue_newsletter_message(self.scheduled_newsletter_message.hashid)
        process_outgoing_message_queue()
        self.assertEquals(len(mail.outbox), num_subscribers)

    def test_if_scheduled_for_past_date_sends_immediately(self):
        people = []
        num_subscribers = Factory.rand_int(end=20)
        for i in range(0, num_subscribers):
            s = Factory.subscription(newsletter=self.newsletter)
            s.double_opt_in()
            people.append(s)

        self.scheduled_newsletter_message = Factory.scheduled_newsletter_message(
            newsletter=self.newsletter,
            send_at_date=self.now() - datetime.timedelta(days=2),
            send_at_hour=self.now().hour,
            send_at_minute=self.now().minute,
            use_local_time=False,
        )
        self.subject = self.scheduled_newsletter_message.message.subject
        self.body = self.scheduled_newsletter_message.message.body_text_unrendered
        queue_newsletter_message(self.scheduled_newsletter_message.hashid)
        process_outgoing_message_queue()
        self.assertEquals(len(mail.outbox), num_subscribers)

    @unittest.skip("For time zones")
    def test_time_zones_sends_in_separate_batches(self):
        self.assertEquals(False, "Test written")
