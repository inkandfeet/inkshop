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
from clubhouse.models import StaffMember


@render_to("clubhouse/dashboard.html")
@login_required
def dashboard(request):
    page_name = "dashboard"
    return locals()


@render_to("clubhouse/messages.html")
@login_required
def messages(request):
    page_name = "messages"
    messages = Message.objects.all()
    return locals()


@render_to("clubhouse/message.html")
@login_required
def message(request, hashid):
    page_name = "messages"
    message = Message.objects.get(hashid=hashid)
    return locals()


@render_to("clubhouse/people.html")
@login_required
def people(request):
    page_name = "people"
    people = Person.objects.all()
    return locals()


@render_to("clubhouse/person.html")
@login_required
def person(request, hashid):
    page_name = "people"
    p = Person.objects.get(hashid=hashid)
    return locals()


@render_to("clubhouse/newsletters.html")
@login_required
def newsletters(request):
    page_name = "newsletters"
    Newsletter.objects.all()
    return locals()


@render_to("clubhouse/newsletter.html")
@login_required
def newsletter(request, hashid):
    page_name = "newsletters"
    Newsletter.objects.get(hashid=hashid)
    return locals()


@render_to("clubhouse/scheduled_newsletters.html")
@login_required
def scheduled_newsletters(request):
    page_name = "scheduled_newsletters"
    snms = ScheduledNewsletterMessage.objects.all()
    return locals()


@render_to("clubhouse/scheduled_newsletter.html")
@login_required
def scheduled_newsletter(request, hashid):
    page_name = "scheduled_newsletters"
    snm = ScheduledNewsletterMessage.objects.get(hashid=hashid)
    return locals()
