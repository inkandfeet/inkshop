import mock
import unittest
from django.test import TestCase
from django.utils import timezone


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
