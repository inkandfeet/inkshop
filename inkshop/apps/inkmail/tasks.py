import datetime
import json
import logging
import requests
from binascii import hexlify
from simplecrypt import encrypt

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from celery.task import task, periodic_task
from django.utils import timezone


@periodic_task(run_every=datetime.timedelta(seconds=5), expires=10)
def hello():
    message = "Hi at %s" % timezone.now()
    print(message)
