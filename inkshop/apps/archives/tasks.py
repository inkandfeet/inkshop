import json
import requests

from django.conf import settings
from inkmail.helpers import send_mail
from django.template.loader import render_to_string
from celery.task import task
