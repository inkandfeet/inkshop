import logging
import json

from utils.helpers import reverse
from django.core import mail
from django.conf import settings
from django.test.utils import override_settings

from people.models import Person
from archives.models import HistoricalEvent
from inkmail.models import Subscription, OutgoingMessage
from inkmail.tasks import process_outgoing_message_queue
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
                host='mail',
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
                host='mail',
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
                host='mail',
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
                host='mail',
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
                host='mail',
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
                host='mail',
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
                host='mail',
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
                host='mail',
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
                host='mail',
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
                host='mail',
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
                host='mail',
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
                host='mail',
            ),
            {
                'first_name': name,
                'email': email,
                'newsletter': self.newsletter.internal_name,
                'subscription_url': subscription_url,
            },
        )
        self.assertEquals(response.status_code, 200)
        process_outgoing_message_queue()

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, self.newsletter.confirm_message.subject)
        self.assertEquals(OutgoingMessage.objects.count(), 1)
        om = OutgoingMessage.objects.all()[0]
        self.assertIn(
            om.render_email_string(self.newsletter.confirm_message.body_text_unrendered),
            mail.outbox[0].alternatives[0][0]
        )
        self.assertIn(
            om.render_email_string(self.newsletter.confirm_message.body_text_unrendered, plain_text=True),
            mail.outbox[0].body
        )
        self.assertEquals(len(mail.outbox[0].to), 1)
        self.assertEquals(mail.outbox[0].to[0], email)
        self.assertEquals(mail.outbox[0].from_email, self.newsletter.full_from_email)


class TestWelcomeEmail(MockRequestsTestCase):

    def setUp(self, *args, **kwargs):
        self.newsletter = Factory.newsletter()
        super(TestWelcomeEmail, self).setUp(*args, **kwargs)

    def test_post_subscribe_200(self):
        email = Factory.rand_email()
        name = Factory.rand_name()
        subscription_url = Factory.rand_url()
        response = self.post(
            reverse(
                'inkmail:subscribe',
                host='mail',
            ),
            {
                'first_name': name,
                'email': email,
                'newsletter': self.newsletter.internal_name,
                'subscription_url': subscription_url,
            },
        )
        self.assertEquals(response.status_code, 200)
        process_outgoing_message_queue()

        s = Subscription.objects.all()[0]
        self.get(s.opt_in_link)
        process_outgoing_message_queue()

        self.assertEquals(len(mail.outbox), 2)
        self.assertEquals(mail.outbox[1].subject, self.newsletter.welcome_message.subject)
        om = OutgoingMessage.objects.all()[0]
        self.assertIn(
            om.render_email_string(self.newsletter.welcome_message.body_text_unrendered),
            mail.outbox[1].alternatives[0][0]
        )
        self.assertIn(
            om.render_email_string(self.newsletter.welcome_message.body_text_unrendered, plain_text=True),
            mail.outbox[1].body
        )
        self.assertEquals(len(mail.outbox[1].to), 1)
        self.assertEquals(mail.outbox[1].to[0], email)
        self.assertEquals(mail.outbox[1].from_email, self.newsletter.full_from_email)


@override_settings(DISABLE_ENCRYPTION_FOR_TESTS=False)
class TestHistoricalEvent(MockRequestsTestCase):

    def setUp(self, *args, **kwargs):
        self.newsletter = Factory.newsletter()
        super(TestHistoricalEvent, self).setUp(*args, **kwargs)

    def test_post_subscribe_200(self):
        email = Factory.rand_email()
        name = Factory.rand_name()
        subscription_url = Factory.rand_url()
        response = self.post(
            reverse(
                'inkmail:subscribe',
                host='mail',
            ),
            {
                'first_name': name,
                'email': email,
                'newsletter': self.newsletter.internal_name,
                'subscription_url': subscription_url,
            },
        )
        self.assertEquals(response.status_code, 200)
        self.assertEquals(HistoricalEvent.objects.count(), 1)
        self.assertEquals(Person.objects.count(), 1)
        self.assertEquals(Subscription.objects.count(), 1)
        he = HistoricalEvent.objects.all()[0]
        p = Person.objects.all()[0]
        s = Subscription.objects.all()[0]
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
