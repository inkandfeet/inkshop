import json
import requests

from django.conf import settings
from django.template.loader import render_to_string
from celery.task import task

from inkmail.helpers import send_message
