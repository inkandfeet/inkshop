
import mock
import unittest
from django.test import TestCase
from django.utils import timezone
from utils.factory import Factory
from inkmail.tasks import process_outgoing_message_queue
from inkmail.helpers import queue_message, queue_newsletter_message, queue_transactional_message
from inkmail.models import OutgoingMessage


class MockRequests(object):
    def __init__(self, *args, **kwargs):
        if args:
            self.data = args[0]

    status_code = 200
    response = {"success": True}

    @property
    def content(self):
        return self.data or ""


def mock_requests(url, data):
    return MockRequests(data)


class MockRequestsTestCase(TestCase):

    def setUp(self):
        self.start_time = self.now()
        self.maxDiff = None
        self.patches = {
            "requests.patch": mock_requests,
            "requests.put": mock_requests,
            "requests.post": mock_requests,
            "requests.get": mock_requests,
        }

        self.applied_patches = [mock.patch(patch, data) for patch, data in self.patches.items()]
        for patch in self.applied_patches:
            patch.start()

    def tearDown(self):
        for patch in self.applied_patches:
            patch.stop()

    def now(self):
        return timezone.now()

    def assertBasicallyEqualTimes(self, t1, t2):  # noqa
        # self.assertEquals(t1.tzinfo, t2.tzinfo)
        diff = abs((t2 - t1).total_seconds())
        self.assertTrue(diff < 1)

    def post(self, *args, **kwargs):
        self._source_ip = Factory.rand_ip()
        return self.client.post(HTTP_X_FORWARDED_FOR=self._source_ip, *args, **kwargs)

    def get(self, *args, **kwargs):
        self._source_ip = Factory.rand_ip()
        return self.client.post(HTTP_X_FORWARDED_FOR=self._source_ip, *args, **kwargs)


class MailTestCase(MockRequestsTestCase):
    def setUp(self, *args, **kwargs):
        super(MailTestCase, self).setUp(*args, **kwargs)

    def create_subscribed_person(self):
        self.subscription = Factory.subscription()
        self.person = self.subscription.person
        self.newsletter = self.subscription.newsletter
        self.subscription.double_opt_in()

    def create_transactional_person(self):
        self.person = Factory.person()

    def send_test_message(self):
        self.test_message = Factory.message()
        self.subject = self.test_message.subject
        self.body_unrendered = self.test_message.body_text_unrendered
        queue_message(message=self.test_message, subscription=self.subscription)
        om = OutgoingMessage.objects.get(person=self.person, message=self.test_message,)
        self.body = om.render_email_string(self.test_message.body_text_unrendered)
        process_outgoing_message_queue()

    def send_newsletter_message(self):
        self.scheduled_newsletter_message = Factory.scheduled_newsletter_message(
            newsletter=self.newsletter,
            send_at_date=self.now(),
            send_at_hour=self.now().hour,
            send_at_minute=self.now().minute,
            use_local_time=False,
        )
        self.subject = self.scheduled_newsletter_message.message.subject
        self.body_unrendered = self.scheduled_newsletter_message.message.body_text_unrendered
        queue_newsletter_message(scheduled_newsletter_message=self.scheduled_newsletter_message)
        process_outgoing_message_queue()

    def send_test_transactional_message(self):
        self.transactional_message = Factory.message(person=self.person, transactional=True)
        self.subject = self.transactional_message.subject
        self.body = self.transactional_message.body_text_unrendered
        self.body_unrendered = self.transactional_message.body_text_unrendered
        queue_transactional_message(message=self.transactional_message, person=self.person)
        om = OutgoingMessage.objects.get(person=self.person, message=self.transactional_message,)
        self.body = om.render_email_string(self.transactional_message.body_text_unrendered)
        process_outgoing_message_queue()
