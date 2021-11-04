from freezegun import freeze_time
import datetime
import logging
import json
import mock
import unittest

from utils.helpers import reverse
from django.core import mail
from django.conf import settings
from django.test.utils import override_settings

from people.models import Person
from inkmail.models import Subscription
from inkmail.tasks import process_outgoing_message_queue
from utils.factory import Factory
from utils.test_helpers import MailTestCase
from utils.encryption import normalize_lower_and_encrypt, normalize_and_encrypt, encrypt, decrypt


class TestResetPassword(MailTestCase):

    def setUp(self, *args, **kwargs):
        self.person = Factory.person()
        self.pw = Factory.rand_str(include_emoji=False)
        self.person.set_password(self.pw)
        super(TestResetPassword, self).setUp(*args, **kwargs)

    def test_reset_flow(self):
        new_password = Factory.rand_str(length=20, include_emoji=False)

        resp = self.get(
            reverse('admin_password_reset'),
            # reverse('password_reset_confirm')
            follow=True,
        )

        self.assertTrue(b"id_email" in resp.content)
        resp = self.post(
            reverse('admin_password_reset'),
            {
                'email': self.person.email,
            },
            follow=True
        )

        self.assertTrue(b"A link is on its way" in resp.content)

        self.assertEquals(len(mail.outbox), 1)
        message = mail.outbox[0]

        body = message.body

        self.assertIn("/password-reset/", body)
        reset_index = body.find("/password-reset/") + len("/password-reset/")
        uid_index_ends = body.find("/", reset_index)
        token_index_ends = body.find("/", uid_index_ends + 1)

        uid = body[reset_index:uid_index_ends]
        token = body[uid_index_ends + 1:token_index_ends]
        reset_url = "/accounts/password-reset/%s/%s" % (uid, token,)
        resp = self.get(
            # reverse('password_reset_confirm', args=(uid, token,)),
            reset_url,
            follow=True,
        )
        self.assertIn(b"your new password", resp.content)
        resp = self.post(
            "/accounts/password-reset/%s/set-password/" % uid,
            {
                "new_password1": new_password,
                "new_password2": new_password,
                # "csrfmiddlewaretoken": csrf_token,
                # "next": "/products/",
            },
            follow=True,
        )

        self.assertIn(b"Your new password has been saved.", resp.content)
        resp = self.post(
            "/accounts/login/",
            {
                "username": self.person.email,
                "password": new_password,
                "next": "/products/"
            },
            follow=True,
        )
        self.assertIn(b"logout_link", resp.content)
