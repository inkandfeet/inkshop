import logging
import json

from django.urls import reverse
from django.core import mail
from django.conf import settings
from django.test.utils import override_settings

from people.models import Person
from utils.factory import Factory
from utils.test_helpers import MockRequestsTestCase
from utils.encryption import normalize_lower_and_encrypt, normalize_and_encrypt, encrypt, decrypt
import mock
import unittest

from inkmail.models import Subscription
from inkmail.helpers import send_mail, send_even_if_not_double_opted_in, send_transactional_email
from inkmail.helpers import send_message, send_transactional_message


class MailTestCase(MockRequestsTestCase):
    def setUp(self, *args, **kwargs):
        self.subscription = Factory.subscription()
        self.person = self.subscription.person
        self.newsletter = self.subscription.newsletter
        self.message = Factory.message(newsletter=self.newsletter)
        super(MailTestCase, self).setUp(*args, **kwargs)

    def send_test_mail(self):
        self.subject = Factory.rand_text()
        self.body = Factory.rand_text(words=150)
        send_mail(self.subscription.pk, self.subject, self.body)

    def send_test_even_if_not_double_opted_in(self):
        self.subject = Factory.rand_text()
        self.body = Factory.rand_text(words=150)
        send_even_if_not_double_opted_in(self.subscription.pk, self.subject, self.body)

    def send_test_transactional_email(self):
        self.subject = Factory.rand_text()
        self.body = Factory.rand_text(words=150)
        send_transactional_email(self.subscription.pk, self.subject, self.body)

    def send_test_message(self):
        send_message(self.message.pk, self.subscription.pk)

    def send_test_transactional_message(self):
        send_transactional_message(self.message.pk, self.subscription.pk)


class TestSendMail(MailTestCase):

    def test_send_mail_sends_to_valid_subscriber(self):
        self.subscription.double_opt_in()
        self.send_test_mail()

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, self.subject)
        self.assertEquals(mail.outbox[0].body, self.body)
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(mail.outbox[0].to[0], self.person.email)
        self.assertEquals(mail.outbox[0].from_email, self.newsletter.full_from_email)

    def test_send_mail_does_not_send_to_unsubscribed(self):
        self.subscription.double_opt_in()
        self.subscription.unsubscribe()
        self.send_test_mail()
        self.assertEquals(len(mail.outbox), 0)

    def test_send_mail_does_not_send_to_not_double_opted_in(self):
        self.send_test_mail()
        self.assertEquals(len(mail.outbox), 0)

    def test_send_mail_still_sends_to_trolls(self):
        self.subscription.double_opt_in()
        self.person.mark_troll()
        self.send_test_mail()

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, self.subject)
        self.assertEquals(mail.outbox[0].body, self.body)
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(mail.outbox[0].to[0], self.person.email)
        self.assertEquals(mail.outbox[0].from_email, self.newsletter.full_from_email)

    def test_send_mail_does_not_send_to_banned_people(self):
        self.subscription.double_opt_in()
        self.person.ban()
        self.send_test_mail()
        self.assertEquals(len(mail.outbox), 0)

    def test_send_mail_does_not_send_to_hard_bounce(self):
        self.subscription.double_opt_in()
        m = Factory.message()
        self.person.hard_bounce(message=m)
        self.send_test_mail()
        self.assertEquals(len(mail.outbox), 0)

    def test_send_mail_does_not_send_to_hard_bounce_even_if_message_missing(self):
        self.subscription.double_opt_in()
        self.person.hard_bounce()
        self.send_test_mail()
        self.assertEquals(len(mail.outbox), 0)


class TestTransactionalMail(MailTestCase):

    def test_send_transactional_mail_sends_to_valid_subscriber(self):
        self.subscription.double_opt_in()
        self.send_test_transactional_email()

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, self.subject)
        self.assertEquals(mail.outbox[0].body, self.body)
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(mail.outbox[0].to[0], self.person.email)
        self.assertEquals(mail.outbox[0].from_email, self.newsletter.full_from_email)

    def test_send_transactional_mail_sends_to_unsubscribed(self):
        self.subscription.double_opt_in()
        self.subscription.unsubscribe()
        self.send_test_transactional_email()

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, self.subject)
        self.assertEquals(mail.outbox[0].body, self.body)
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(mail.outbox[0].to[0], self.person.email)
        self.assertEquals(mail.outbox[0].from_email, self.newsletter.full_from_email)

    def test_send_transactional_mail_sends_to_not_double_opted_in(self):
        self.send_test_transactional_email()
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, self.subject)
        self.assertEquals(mail.outbox[0].body, self.body)
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(mail.outbox[0].to[0], self.person.email)
        self.assertEquals(mail.outbox[0].from_email, self.newsletter.full_from_email)

    def test_send_transactional_mail_sends_to_trolls(self):
        self.subscription.double_opt_in()
        self.person.mark_troll()
        self.send_test_transactional_email()

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, self.subject)
        self.assertEquals(mail.outbox[0].body, self.body)
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(mail.outbox[0].to[0], self.person.email)
        self.assertEquals(mail.outbox[0].from_email, self.newsletter.full_from_email)

    def test_send_transactional_mail_does_not_send_to_banned_people(self):
        self.subscription.double_opt_in()
        self.person.ban()
        self.send_test_transactional_email()
        self.assertEquals(len(mail.outbox), 0)

    def test_send_transactional_mail_does_not_send_to_hard_bounce(self):
        self.subscription.double_opt_in()
        m = Factory.message()
        self.person.hard_bounce(message=m)
        self.send_test_transactional_email()
        self.assertEquals(len(mail.outbox), 0)

    def test_send_transactional_mail_does_not_send_to_hard_bounce_even_if_message_missing(self):
        self.subscription.double_opt_in()
        self.person.hard_bounce()
        self.send_test_transactional_email()
        self.assertEquals(len(mail.outbox), 0)


class TestSendMessageMail(MailTestCase):

    def test_send_messsage_sends_to_valid_subscriber(self):
        self.subscription.double_opt_in()
        self.send_test_messsage()
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, self.subject)
        self.assertEquals(mail.outbox[0].body, self.body)
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(mail.outbox[0].to[0], self.person.email)
        self.assertEquals(mail.outbox[0].from_email, self.newsletter.full_from_email)

    def test_send_messsage_does_not_send_to_unsubscribed(self):
        self.subscription.double_opt_in()
        self.subscription.unsubscribe()
        self.send_test_messsage()
        self.assertEquals(len(mail.outbox), 0)

    def test_send_messsage_does_not_send_to_not_double_opted_in(self):
        self.send_test_messsage()
        self.assertEquals(len(mail.outbox), 0)

    def test_send_messsage_still_sends_to_trolls(self):
        self.subscription.double_opt_in()
        self.person.mark_troll()
        self.send_test_messsage()
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, self.subject)
        self.assertEquals(mail.outbox[0].body, self.body)
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(mail.outbox[0].to[0], self.person.email)
        self.assertEquals(mail.outbox[0].from_email, self.newsletter.full_from_email)

    def test_send_messsage_does_not_send_to_banned_people(self):
        self.subscription.double_opt_in()
        self.person.ban()
        self.send_test_messsage()
        self.assertEquals(len(mail.outbox), 0)

    def test_send_messsage_does_not_send_to_hard_bounce(self):
        self.subscription.double_opt_in()
        m = Factory.message()
        self.person.hard_bounce(message=m)
        self.send_test_messsage()
        self.assertEquals(len(mail.outbox), 0)

    def test_send_messsage_does_not_send_to_hard_bounce_even_if_message_missing(self):
        self.subscription.double_opt_in()
        self.person.hard_bounce()
        self.send_test_messsage()
        self.assertEquals(len(mail.outbox), 0)


class TestSendTransactionalMessageMail(MailTestCase):

    def test_send_transactional_message_sends_to_valid_subscriber(self):
        self.subscription.double_opt_in()
        self.send_test_transactional_message()

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, self.subject)
        self.assertEquals(mail.outbox[0].body, self.body)
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(mail.outbox[0].to[0], self.person.email)
        self.assertEquals(mail.outbox[0].from_email, self.newsletter.full_from_email)

    def test_send_transactional_message_sends_to_unsubscribed(self):
        self.subscription.double_opt_in()
        self.subscription.unsubscribe()
        self.send_test_transactional_message()

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, self.subject)
        self.assertEquals(mail.outbox[0].body, self.body)
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(mail.outbox[0].to[0], self.person.email)
        self.assertEquals(mail.outbox[0].from_email, self.newsletter.full_from_email)

    def test_send_transactional_message_sends_to_not_double_opted_in(self):
        self.send_test_transactional_message()
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, self.subject)
        self.assertEquals(mail.outbox[0].body, self.body)
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(mail.outbox[0].to[0], self.person.email)
        self.assertEquals(mail.outbox[0].from_email, self.newsletter.full_from_email)

    def test_send_transactional_message_sends_to_trolls(self):
        self.subscription.double_opt_in()
        self.person.mark_troll()
        self.send_test_transactional_message()

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, self.subject)
        self.assertEquals(mail.outbox[0].body, self.body)
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(mail.outbox[0].to[0], self.person.email)
        self.assertEquals(mail.outbox[0].from_email, self.newsletter.full_from_email)

    def test_send_transactional_message_does_not_send_to_banned_people(self):
        self.subscription.double_opt_in()
        self.person.ban()
        self.send_test_transactional_message()
        self.assertEquals(len(mail.outbox), 0)

    def test_send_transactional_message_does_not_send_to_hard_bounce(self):
        self.subscription.double_opt_in()
        m = Factory.message()
        self.person.hard_bounce(message=m)
        self.send_test_transactional_message()
        self.assertEquals(len(mail.outbox), 0)

    def test_send_transactional_message_does_not_send_to_hard_bounce_even_if_message_missing(self):
        self.subscription.double_opt_in()
        self.person.hard_bounce()
        self.send_test_transactional_message()
        self.assertEquals(len(mail.outbox), 0)
