# -*- coding: utf-8 -*-

from base64 import b64decode
import datetime
import json
import logging
import time

from django.conf import settings
from django.core.mail import mail_admins
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from annoying.decorators import render_to, ajax_request
from people.models import Person
from inkmail.models import ScheduledNewsletterMessage, Message, OutgoingMessage, Newsletter
from clubhouse.model import StaffMember


@render_to("clubhouse/home.html")
@login_required
def home(request):
    return locals()


@render_to("clubhouse/messages.html")
@login_required
def messages(request):
    messages = Message.objects.all()
    return locals()


@render_to("clubhouse/message.html")
@login_required
def message(request, hashid):
    message = Message.objects.get(hashid=hashid)
    return locals()


@render_to("clubhouse/people.html")
@login_required
def people(request):
    people = Person.objects.all()
    return locals()


@render_to("clubhouse/person.html")
@login_required
def person(request, hashid):
    p = Person.objects.get(hashid=hashid)
    return locals()


@render_to("clubhouse/newsletters.html")
@login_required
def newsletters(request):
    Newsletter.objects.all()
    return locals()


@render_to("clubhouse/newsletter.html")
@login_required
def newsletter(request, hashid):
    Newsletter.objects.get(hashid=hashid)
    return locals()


@render_to("clubhouse/scheduled_newsletters.html")
@login_required
def scheduled_newsletters(request, hashid):
    snms = ScheduledNewsletterMessage.objects.all()
    return locals()


@render_to("clubhouse/scheduled_newsletter.html")
@login_required
def scheduled_newsletter(request, hashid):
    snm = ScheduledNewsletterMessage.objects.get(hashid=hashid)
    return locals()
