import logging
import json

from utils.helpers import reverse
from django.core import mail
from django.conf import settings
from django.test.utils import override_settings

from people.models import Person
from utils.factory import Factory
from utils.test_helpers import MockRequestsTestCase, MailTestCase
from utils.encryption import normalize_lower_and_encrypt, normalize_and_encrypt, encrypt, decrypt
import mock
import unittest

from inkmail.models import Subscription, OutgoingMessage


class TestSendMessageMail(MailTestCase):

    def setUp(self, *args, **kwargs):
        self.create_subscribed_person()
        super(TestSendMessageMail, self).setUp(*args, **kwargs)

    def test_send_messsage_sends_to_valid_subscriber(self):
        self.subscription.double_opt_in()
        self.send_test_message()
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, self.test_message.subject)
        om = OutgoingMessage.objects.get(person=self.person, message=self.test_message,)
        self.assertIn(
            om.render_email_string(self.test_message.body_text_unrendered)[:-10],
            mail.outbox[0].alternatives[0][0]
        )
        self.assertIn(
            om.render_email_string(self.test_message.body_text_unrendered, plain_text=True)[:-10],
            mail.outbox[0].body
        )
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(mail.outbox[0].to[0], self.person.email)
        self.assertEquals(mail.outbox[0].from_email, self.newsletter.full_from_email)

    def test_send_messsage_does_not_send_to_unsubscribed(self):
        self.subscription.double_opt_in()
        self.subscription.unsubscribe()
        self.send_test_message()
        self.assertEquals(len(mail.outbox), 0)

    def test_send_messsage_does_not_send_to_not_double_opted_in(self):
        self.subscription.double_opted_in = False
        self.subscription.double_opted_in_at = None
        self.subscription.save()
        self.send_test_message()
        self.assertEquals(len(mail.outbox), 0)

    def test_send_messsage_still_sends_to_trolls(self):
        self.subscription.double_opt_in()
        self.person.mark_troll()
        self.send_test_message()
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, self.test_message.subject)
        om = OutgoingMessage.objects.get(person=self.person, message=self.test_message,)
        self.assertIn(
            om.render_email_string(self.test_message.body_text_unrendered)[:-10],
            mail.outbox[0].alternatives[0][0]
        )
        self.assertIn(
            om.render_email_string(self.test_message.body_text_unrendered, plain_text=True)[:-10],
            mail.outbox[0].body
        )
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(mail.outbox[0].to[0], self.person.email)
        self.assertEquals(mail.outbox[0].from_email, self.newsletter.full_from_email)

    def test_send_messsage_does_not_send_to_banned_people(self):
        self.subscription.double_opt_in()
        self.person.ban()
        self.send_test_message()
        self.assertEquals(len(mail.outbox), 0)

    def test_send_messsage_does_not_send_to_hard_bounce(self):
        self.subscription.double_opt_in()
        m = Factory.message()
        self.person.hard_bounce(bouncing_message=m)
        self.send_test_message()
        self.assertEquals(len(mail.outbox), 0)

    def test_send_messsage_does_not_send_to_hard_bounce_even_if_message_missing(self):
        self.subscription.double_opt_in()
        self.person.hard_bounce()
        self.send_test_message()
        self.assertEquals(len(mail.outbox), 0)


class TestSendNewsletterMessageMail(MailTestCase):

    def setUp(self, *args, **kwargs):
        self.create_subscribed_person()
        super(TestSendNewsletterMessageMail, self).setUp(*args, **kwargs)

    def test_send_messsage_sends_to_valid_subscriber(self):
        self.subscription.double_opt_in()
        self.send_newsletter_message()
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, self.subject)
        om = OutgoingMessage.objects.get(person=self.person, message=self.scheduled_newsletter_message.message,)
        self.assertIn(
            om.render_email_string(self.scheduled_newsletter_message.message.body_text_unrendered)[:-10],
            mail.outbox[0].alternatives[0][0]
        )
        self.assertIn(
            om.render_email_string(self.scheduled_newsletter_message.message.body_text_unrendered, plain_text=True)[:-10],
            mail.outbox[0].body
        )
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(mail.outbox[0].to[0], self.person.email)
        self.assertEquals(mail.outbox[0].from_email, self.newsletter.full_from_email)

    def test_send_messsage_does_not_send_to_unsubscribed(self):
        self.subscription.double_opt_in()
        self.subscription.unsubscribe()
        self.send_newsletter_message()
        self.assertEquals(len(mail.outbox), 0)

    def test_send_messsage_does_not_send_to_not_double_opted_in(self):
        self.subscription.double_opted_in = False
        self.subscription.double_opted_in_at = None
        self.subscription.save()
        self.send_newsletter_message()
        self.assertEquals(len(mail.outbox), 0)

    def test_send_messsage_still_sends_to_trolls(self):
        self.subscription.double_opt_in()
        self.person.mark_troll()
        self.send_newsletter_message()
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, self.subject)
        om = OutgoingMessage.objects.get(person=self.person, message=self.scheduled_newsletter_message.message,)
        self.assertIn(
            om.render_email_string(self.scheduled_newsletter_message.message.body_text_unrendered)[:-10],
            mail.outbox[0].alternatives[0][0]
        )
        self.assertIn(
            om.render_email_string(self.scheduled_newsletter_message.message.body_text_unrendered, plain_text=True)[:-10],
            mail.outbox[0].body
        )
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(mail.outbox[0].to[0], self.person.email)
        self.assertEquals(mail.outbox[0].from_email, self.newsletter.full_from_email)

    def test_send_messsage_does_not_send_to_banned_people(self):
        self.subscription.double_opt_in()
        self.person.ban()
        self.send_newsletter_message()
        self.assertEquals(len(mail.outbox), 0)

    def test_send_messsage_does_not_send_to_hard_bounce(self):
        self.subscription.double_opt_in()
        m = Factory.message()
        self.person.hard_bounce(bouncing_message=m)
        self.send_newsletter_message()
        self.assertEquals(len(mail.outbox), 0)

    def test_send_messsage_does_not_send_to_hard_bounce_even_if_message_missing(self):
        self.subscription.double_opt_in()
        self.person.hard_bounce()
        self.send_newsletter_message()
        self.assertEquals(len(mail.outbox), 0)


class TestSendTransactionalMessageToSubcriber(MailTestCase):

    def setUp(self, *args, **kwargs):
        self.create_subscribed_person()
        super(TestSendTransactionalMessageToSubcriber, self).setUp(*args, **kwargs)

    def test_send_transactional_message_sends_to_valid_subscriber(self):
        self.subscription.double_opt_in()
        self.send_test_transactional_message()

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, self.transactional_message.subject)
        om = OutgoingMessage.objects.get(person=self.person, message=self.transactional_message,)
        self.assertIn(
            om.render_email_string(self.transactional_message.body_text_unrendered)[:-10],
            mail.outbox[0].alternatives[0][0]
        )
        self.assertIn(
            om.render_email_string(self.transactional_message.body_text_unrendered, plain_text=True)[:-10],
            mail.outbox[0].body
        )
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(mail.outbox[0].to[0], self.person.email)
        self.assertEquals(mail.outbox[0].from_email, settings.DEFAULT_FROM_EMAIL)

    def test_send_transactional_message_sends_to_unsubscribed(self):
        self.subscription.double_opt_in()
        self.subscription.unsubscribe()
        self.send_test_transactional_message()

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, self.transactional_message.subject)
        om = OutgoingMessage.objects.get(person=self.person, message=self.transactional_message,)
        self.assertIn(
            om.render_email_string(self.transactional_message.body_text_unrendered)[:-10],
            mail.outbox[0].alternatives[0][0]
        )
        self.assertIn(
            om.render_email_string(self.transactional_message.body_text_unrendered, plain_text=True)[:-10],
            mail.outbox[0].body
        )
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(mail.outbox[0].to[0], self.person.email)
        self.assertEquals(mail.outbox[0].from_email, settings.DEFAULT_FROM_EMAIL)

    def test_send_transactional_message_sends_to_not_double_opted_in(self):
        self.send_test_transactional_message()
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, self.transactional_message.subject)
        om = OutgoingMessage.objects.get(person=self.person, message=self.transactional_message,)
        self.assertIn(
            om.render_email_string(self.transactional_message.body_text_unrendered)[:-10],
            mail.outbox[0].alternatives[0][0]
        )
        self.assertIn(
            om.render_email_string(self.transactional_message.body_text_unrendered, plain_text=True)[:-10],
            mail.outbox[0].body
        )
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(mail.outbox[0].to[0], self.person.email)
        self.assertEquals(mail.outbox[0].from_email, settings.DEFAULT_FROM_EMAIL)

    def test_send_transactional_message_sends_to_trolls(self):
        self.subscription.double_opt_in()
        self.person.mark_troll()
        self.send_test_transactional_message()

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, self.transactional_message.subject)
        om = OutgoingMessage.objects.get(person=self.person, message=self.transactional_message,)
        self.assertIn(
            om.render_email_string(self.transactional_message.body_text_unrendered)[:-10],
            mail.outbox[0].alternatives[0][0]
        )
        self.assertIn(
            om.render_email_string(self.transactional_message.body_text_unrendered, plain_text=True)[:-10],
            mail.outbox[0].body
        )
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(mail.outbox[0].to[0], self.person.email)
        self.assertEquals(mail.outbox[0].from_email, settings.DEFAULT_FROM_EMAIL)

    def test_send_transactional_message_does_not_send_to_banned_people(self):
        self.subscription.double_opt_in()
        self.person.ban()
        self.send_test_transactional_message()
        self.assertEquals(len(mail.outbox), 0)

    def test_send_transactional_message_does_not_send_to_hard_bounce(self):
        self.subscription.double_opt_in()
        m = Factory.message()
        self.person.hard_bounce(bouncing_message=m)
        self.send_test_transactional_message()
        self.assertEquals(len(mail.outbox), 0)

    def test_send_transactional_message_does_not_send_to_hard_bounce_even_if_message_missing(self):
        self.subscription.double_opt_in()
        self.person.hard_bounce()
        self.send_test_transactional_message()
        self.assertEquals(len(mail.outbox), 0)


class TestSendTransactionalMessageToNonSubscriber(MailTestCase):

    def setUp(self, *args, **kwargs):
        self.create_transactional_person()
        super(TestSendTransactionalMessageToNonSubscriber, self).setUp(*args, **kwargs)

    def test_send_transactional_message_sends_to_person(self):
        self.send_test_transactional_message()

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, self.transactional_message.subject)
        om = OutgoingMessage.objects.get(person=self.person, message=self.transactional_message,)
        self.assertIn(
            om.render_email_string(self.transactional_message.body_text_unrendered)[:-10],
            mail.outbox[0].alternatives[0][0]
        )
        self.assertIn(
            om.render_email_string(self.transactional_message.body_text_unrendered, plain_text=True)[:-10],
            mail.outbox[0].body
        )
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(mail.outbox[0].to[0], self.person.email)
        self.assertEquals(mail.outbox[0].from_email, settings.DEFAULT_FROM_EMAIL)

    def test_send_transactional_message_sends_to_trolls(self):
        self.person.mark_troll()
        self.send_test_transactional_message()

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, self.transactional_message.subject)
        om = OutgoingMessage.objects.get(person=self.person, message=self.transactional_message,)
        self.assertIn(
            om.render_email_string(self.transactional_message.body_text_unrendered)[:-10],
            mail.outbox[0].alternatives[0][0]
        )
        self.assertIn(
            om.render_email_string(self.transactional_message.body_text_unrendered, plain_text=True)[:-10],
            mail.outbox[0].body
        )
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(mail.outbox[0].to[0], self.person.email)
        self.assertEquals(mail.outbox[0].from_email, settings.DEFAULT_FROM_EMAIL)

    def test_send_transactional_message_does_not_send_to_banned_people(self):
        self.person.ban()
        self.send_test_transactional_message()
        self.assertEquals(len(mail.outbox), 0)

    def test_send_transactional_message_does_not_send_to_hard_bounce(self):
        m = Factory.message()
        self.person.hard_bounce(bouncing_message=m)
        self.send_test_transactional_message()
        self.assertEquals(len(mail.outbox), 0)

    def test_send_transactional_message_does_not_send_to_hard_bounce_even_if_message_missing(self):
        self.person.hard_bounce()
        self.send_test_transactional_message()
        self.assertEquals(len(mail.outbox), 0)
