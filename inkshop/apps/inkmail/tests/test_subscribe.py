import logging
import json

from django.urls import reverse
from django.core import mail
from django.conf import settings
from django.test.utils import override_settings

from people.models import Person
from inkmail.models import Subscription
from utils.factory import Factory
from utils.test_helpers import MockRequestsTestCase
from utils.encryption import normalize_lower_and_encrypt, normalize_and_encrypt, encrypt, decrypt
import mock
import unittest


@unittest.skip("For Friday")
class TestPostSubscribes(MockRequestsTestCase):

    def setUp(self, *args, **kwargs):
        self.newsletter = Factory.newsletter()
        super(TestPostSubscribes, self).setUp(*args, **kwargs)

    def test_post_subscribe_200(self):
        email = Factory.rand_email()
        name = Factory.rand_name()
        response = self.client.post(
            reverse(
                'inkmail:subscribe',
            ),
            {
                'first_name': name,
                'email': email,
                'newsletter': self.newsletter.internal_name,
            },
        )

        self.assertEquals(response.status_code, 200)

    def test_post_subscribe_adds_person_and_subscription(self):
        email = Factory.rand_email()
        name = Factory.rand_name()
        response = self.client.post(
            reverse(
                'inkmail:subscribe',
            ),
            {
                'first_name': name,
                'email': email,
                'newsletter': self.newsletter.internal_name,
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
        self.assertEquals(s.newsletter.name, self.newsletter.name)
        self.assertEquals(s.subscribed_from_url, "http://localhost/mail/subscribe")
        self.assertEquals(s.subscribed_from_ip, "127.0.0.1")

    def test_no_first_name_subscribe_adds_person_and_subscription(self):
        email = Factory.rand_email()
        response = self.client.post(
            reverse(
                'inkmail:subscribe',
            ),
            {
                'email': email,
                'newsletter': self.newsletter.internal_name,
            },
        )

        self.assertEquals(response.status_code, 200)

        self.assertEquals(Person.objects.count(), 1)
        p = Person.objects.all()[0]
        self.assertEquals(p.email, email)

        self.assertEquals(Subscription.objects.count(), 1)
        s = Subscription.objects.all()[0]
        self.assertEquals(s.person, p)
        self.assertEquals(s.newsletter.name, self.newsletter.name)
        self.assertEquals(s.subscribed_from_url, "http://localhost/mail/subscribe")
        self.assertEquals(s.subscribed_from_ip, "127.0.0.1")

    def test_newsletter_required(self):
        email = Factory.rand_email()
        name = Factory.rand_name()
        response = self.client.post(
            reverse(
                'inkmail:subscribe',
            ),
            {
                'first_name': name,
                'email': email,
            },
        )

        self.assertEquals(response.status_code, 422)

        self.assertEquals(Person.objects.count(), 0)
        self.assertEquals(Subscription.objects.count(), 0)

    def test_email_required(self):
        name = Factory.rand_name()
        response = self.client.post(
            reverse(
                'inkmail:subscribe',
            ),
            {
                'first_name': name,
                # 'email': email,
                'newsletter': self.newsletter.internal_name,
            },
        )

        self.assertEquals(response.status_code, 422)

        self.assertEquals(Person.objects.count(), 0)
        self.assertEquals(Subscription.objects.count(), 0)


@unittest.skip("For Friday")
class TestAjaxSubscribes(MockRequestsTestCase):
    def setUp(self, *args, **kwargs):
        self.newsletter = Factory.newsletter()
        super(TestAjaxSubscribes, self).setUp(*args, **kwargs)

    def test_post_subscribe_200(self):
        email = Factory.rand_email()
        name = Factory.rand_name()
        response = self.client.post(
            reverse(
                'inkmail:subscribe',
            ),
            json.dumps({
                'first_name': name,
                'email': email,
                'newsletter': self.newsletter.internal_name,
            }),
            'json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        json_string = response.content.decode('utf-8')
        response_data = json.loads(json_string)
        self.assertEquals(response_data["success"], True)
        self.assertEquals(response.status_code, 200)

    def test_post_subscribe_adds_person_and_subscription(self):
        email = Factory.rand_email()
        name = Factory.rand_name()
        response = self.client.post(
            reverse(
                'inkmail:subscribe',
            ),
            json.dumps({
                'first_name': name,
                'email': email,
                'newsletter': self.newsletter.internal_name,
            }),
            'json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        json_string = response.content.decode('utf-8')
        response_data = json.loads(json_string)
        self.assertEquals(response_data["success"], True)
        self.assertEquals(response.status_code, 200)

        self.assertEquals(Person.objects.count(), 1)
        p = Person.objects.all()[0]
        self.assertEquals(p.first_name, name)
        self.assertEquals(p.email, email)

        self.assertEquals(Subscription.objects.count(), 1)
        s = Subscription.objects.all()[0]
        self.assertEquals(s.person, p)
        self.assertEquals(s.newsletter.name, self.newsletter.name)
        self.assertEquals(s.subscribed_from_url, "http://localhost/mail/subscribe")
        self.assertEquals(s.subscribed_from_ip, "127.0.0.1")

    def test_no_first_name_subscribe_adds_person_and_subscription(self):
        email = Factory.rand_email()
        response = self.client.post(
            reverse(
                'inkmail:subscribe',
            ),
            json.dumps({
                'email': email,
                'newsletter': self.newsletter.internal_name,
            }),
            'json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        json_string = response.content.decode('utf-8')
        response_data = json.loads(json_string)
        self.assertEquals(response_data["success"], True)
        self.assertEquals(response.status_code, 200)

        self.assertEquals(Person.objects.count(), 1)
        p = Person.objects.all()[0]
        self.assertEquals(p.email, email)

        self.assertEquals(Subscription.objects.count(), 1)
        s = Subscription.objects.all()[0]
        self.assertEquals(s.person, p)
        self.assertEquals(s.newsletter.name, self.newsletter.name)
        self.assertEquals(s.subscribed_from_url, "http://localhost/mail/subscribe")
        self.assertEquals(s.subscribed_from_ip, "127.0.0.1")

    def test_newsletter_required(self):
        email = Factory.rand_email()
        name = Factory.rand_name()
        response = self.client.post(
            reverse(
                'inkmail:subscribe',
            ),
            json.dumps({
                'first_name': name,
                'email': email,
            }),
            'json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        json_string = response.content.decode('utf-8')
        response_data = json.loads(json_string)
        self.assertEquals(response_data["success"], False)
        self.assertEquals(response.status_code, 422)

        self.assertEquals(Person.objects.count(), 0)
        self.assertEquals(Subscription.objects.count(), 0)

    def test_email_required(self):
        name = Factory.rand_name()
        response = self.client.post(
            reverse(
                'inkmail:subscribe',
            ),
            json.dumps({
                'first_name': name,
                # 'email': email,
                'newsletter': self.newsletter.internal_name,
            }),
            'json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        json_string = response.content.decode('utf-8')
        response_data = json.loads(json_string)
        self.assertEquals(response_data["success"], False)
        self.assertEquals(response.status_code, 422)

        self.assertEquals(Person.objects.count(), 0)
        self.assertEquals(Subscription.objects.count(), 0)


@unittest.skip("For Friday")
class TestConfirmEmail(MockRequestsTestCase):

    def setUp(self, *args, **kwargs):
        self.newsletter = Factory.newsletter()
        super(TestConfirmEmail, self).setUp(*args, **kwargs)

    def test_post_subscribe_200(self):
        email = Factory.rand_email()
        name = Factory.rand_name()
        response = self.client.post(
            reverse(
                'inkmail:subscribe',
            ),
            {
                'first_name': name,
                'email': email,
                'newsletter': self.newsletter.internal_name,
            },
        )
        self.assertEquals(response.status_code, 200)

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, "Please confirm")
        self.assertEquals(mail.outbox[0].body, "Hi %s firstname Confirm")
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(mail.outbox[0].to[0], email)
        self.assertEquals(mail.outbox[0].from_email, self.newsletter.full_from_email)
