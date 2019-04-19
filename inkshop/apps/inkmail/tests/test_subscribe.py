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


class TestPostSubscribes(MockRequestsTestCase):

    def setUp(self, *args, **kwargs):
        self.newsletter = Factory.newsletter()
        super(TestPostSubscribes, self).setUp(*args, **kwargs)

    def test_post_subscribe_200(self):
        email = Factory.rand_email()
        name = Factory.rand_name()
        subscription_url = Factory.rand_url()
        response = self.post(
            reverse(
                'inkmail:subscribe',
            ),
            {
                'first_name': name,
                'email': email,
                'newsletter': self.newsletter.internal_name,
                'subscription_url': subscription_url,
            },
        )

        self.assertEquals(response.status_code, 200)

    def test_post_subscribe_adds_person_and_subscription(self):
        email = Factory.rand_email()
        name = Factory.rand_name()
        subscription_url = Factory.rand_url()
        response = self.post(
            reverse(
                'inkmail:subscribe',
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
        p = Person.objects.all()[0]
        self.assertEquals(p.first_name, name)
        self.assertEquals(p.email, email)

        self.assertEquals(Subscription.objects.count(), 1)
        s = Subscription.objects.all()[0]
        self.assertEquals(s.person, p)
        self.assertEquals(s.newsletter.name, self.newsletter.name)
        self.assertEquals(s.subscription_url, subscription_url)
        self.assertEquals(s.subscribed_from_ip, self._source_ip)

    def test_no_first_name_subscribe_adds_person_and_subscription(self):
        email = Factory.rand_email()
        subscription_url = Factory.rand_url()
        response = self.post(
            reverse(
                'inkmail:subscribe',
            ),
            {
                'email': email,
                'newsletter': self.newsletter.internal_name,
                'subscription_url': subscription_url,
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
        self.assertEquals(s.subscription_url, subscription_url)
        self.assertEquals(s.subscribed_from_ip, self._source_ip)

    def test_newsletter_required(self):
        email = Factory.rand_email()
        name = Factory.rand_name()
        subscription_url = Factory.rand_url()
        response = self.post(
            reverse(
                'inkmail:subscribe',
            ),
            {
                'first_name': name,
                'email': email,
                'subscription_url': subscription_url,
            },
        )

        self.assertEquals(response.status_code, 422)

        self.assertEquals(Person.objects.count(), 0)
        self.assertEquals(Subscription.objects.count(), 0)

    def test_email_required(self):
        name = Factory.rand_name()
        subscription_url = Factory.rand_url()
        response = self.post(
            reverse(
                'inkmail:subscribe',
            ),
            {
                'first_name': name,
                # 'email': email,
                'newsletter': self.newsletter.internal_name,
                'subscription_url': subscription_url,
            },
        )

        self.assertEquals(response.status_code, 422)

        self.assertEquals(Person.objects.count(), 0)
        self.assertEquals(Subscription.objects.count(), 0)

    def test_subscription_url_required(self):
        name = Factory.rand_name()
        email = Factory.rand_email()
        response = self.post(
            reverse(
                'inkmail:subscribe',
            ),
            {
                'first_name': name,
                'email': email,
                'newsletter': self.newsletter.internal_name,
                # 'subscription_url': subscription_url,
            },
        )

        self.assertEquals(response.status_code, 422)

        self.assertEquals(Person.objects.count(), 0)
        self.assertEquals(Subscription.objects.count(), 0)


class TestAjaxSubscribes(MockRequestsTestCase):
    def setUp(self, *args, **kwargs):
        self.newsletter = Factory.newsletter()
        super(TestAjaxSubscribes, self).setUp(*args, **kwargs)

    def test_post_subscribe_200(self):
        email = Factory.rand_email()
        name = Factory.rand_name()
        subscription_url = Factory.rand_url()
        response = self.post(
            reverse(
                'inkmail:subscribe',
            ),
            json.dumps({
                'first_name': name,
                'email': email,
                'newsletter': self.newsletter.internal_name,
                'subscription_url': subscription_url,
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
        subscription_url = Factory.rand_url()
        response = self.post(
            reverse(
                'inkmail:subscribe',
            ),
            json.dumps({
                'first_name': name,
                'email': email,
                'newsletter': self.newsletter.internal_name,
                'subscription_url': subscription_url,
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
        self.assertEquals(s.subscription_url, subscription_url)
        self.assertEquals(s.subscribed_from_ip, self._source_ip)

    def test_no_first_name_subscribe_adds_person_and_subscription(self):
        email = Factory.rand_email()
        subscription_url = Factory.rand_url()
        response = self.post(
            reverse(
                'inkmail:subscribe',
            ),
            json.dumps({
                'email': email,
                'newsletter': self.newsletter.internal_name,
                'subscription_url': subscription_url,
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
        self.assertEquals(s.subscription_url, subscription_url)
        self.assertEquals(s.subscribed_from_ip, self._source_ip)

    def test_newsletter_required(self):
        email = Factory.rand_email()
        name = Factory.rand_name()
        subscription_url = Factory.rand_url()
        response = self.post(
            reverse(
                'inkmail:subscribe',
            ),
            json.dumps({
                'first_name': name,
                'email': email,
                'subscription_url': subscription_url,
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
        subscription_url = Factory.rand_url()
        response = self.post(
            reverse(
                'inkmail:subscribe',
            ),
            json.dumps({
                'first_name': name,
                # 'email': email,
                'newsletter': self.newsletter.internal_name,
                'subscription_url': subscription_url,
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


class TestConfirmEmail(MockRequestsTestCase):

    def setUp(self, *args, **kwargs):
        self.newsletter = Factory.newsletter()
        super(TestConfirmEmail, self).setUp(*args, **kwargs)

    def test_post_subscribe_200(self):
        email = Factory.rand_email()
        name = Factory.rand_name()
        subscription_url = Factory.rand_url()
        response = self.post(
            reverse(
                'inkmail:subscribe',
            ),
            {
                'first_name': name,
                'email': email,
                'newsletter': self.newsletter.internal_name,
                'subscription_url': subscription_url,
            },
        )
        self.assertEquals(response.status_code, 200)

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, self.newsletter.confirm_message.subject)
        self.assertEquals(mail.outbox[0].body, self.newsletter.confirm_message.body_text_unrendered)
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(mail.outbox[0].to[0], email)
        self.assertEquals(mail.outbox[0].from_email, self.newsletter.full_from_email)
