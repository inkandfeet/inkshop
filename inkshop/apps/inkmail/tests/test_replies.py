import logging
import json

from django.urls import reverse
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


class TestReplyBasics(MailTestCase):

    def setUp(self, *args, **kwargs):
        self.newsletter = Factory.newsletter()
        super(TestReplyBasics, self).setUp(*args, **kwargs)

    def test_reply_address_is_correct(self):
        s = Factory.subscription(newsletter=self.newsletter)
        s.double_opt_in()
        self.send_newsletter_message()

        self.assertEquals(len(mail.outbox), 1)
        m = mail.outbox[0]
        print(m.__dict__)
        self.assertEquals(m.reply_to, "%s <%s>" % (self.newsletter.from_name, self.newsletter.from_email))
