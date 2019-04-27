import logging
import json

from django_hosts.resolvers import reverse
from django.core import mail
from django.conf import settings
from django.test.utils import override_settings

from utils.factory import Factory
import mock
import unittest
