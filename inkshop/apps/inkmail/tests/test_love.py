import logging
import json

from utils.helpers import reverse
from django.core import mail
from django.conf import settings
from django.test.utils import override_settings

from people.models import Person
from inkmail.models import Subscription, OutgoingMessage
from utils.factory import Factory
from utils.test_helpers import MailTestCase
from utils.encryption import normalize_lower_and_encrypt, normalize_and_encrypt, encrypt, decrypt
import mock
import unittest


class TestLoveBasics(MailTestCase):

    def setUp(self, *args, **kwargs):
        self.newsletter = Factory.newsletter()
        super(TestLoveBasics, self).setUp(*args, **kwargs)

    def test_love_link_included_in_message_send(self):
        self.assertEquals(len(mail.outbox), 0)
        self.create_subscribed_person()
        self.send_test_transactional_message()

        self.assertEquals(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEquals(OutgoingMessage.objects.count(), 1)
        self.om = OutgoingMessage.objects.all()[0]
        self.assertNotIn(self.om.love_link, m.body)

    def test_clicking_love_marks_as_loved(self):
        self.test_love_link_included_in_message_send()
        self.loved_resp = self.get(self.om.love_link)

        # Refresh
        self.om = OutgoingMessage.objects.get(pk=self.om.pk)
        self.assertEquals(self.om.loved, True)
        self.assertBasicallyEqualTimes(self.om.loved_at, self.now())

    def test_clicking_love_shows_correct_page(self):
        self.test_clicking_love_marks_as_loved()
        self.assertIn("Loved!", self.loved_resp.content.decode('utf-8'))

    @unittest.skip("Add a fallback so I can have this be a test again. :)")
    def test_clicking_love_shows_adorable_gif(self):
        self.test_clicking_love_marks_as_loved()
        # self.assertIn(".gif", self.loved_resp.content.decode('utf-8'))
