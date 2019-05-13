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
from django.shortcuts import redirect
from utils.helpers import reverse
from django.views.decorators.csrf import csrf_exempt

from annoying.decorators import render_to, ajax_request
from people.models import Person
from inkmail.models import ScheduledNewsletterMessage, Message, OutgoingMessage, Newsletter, Subscription
from inkmail.models import Organization
from inkmail.forms import ScheduledNewsletterMessageForm, MessageForm, OutgoingMessageForm
from inkmail.forms import NewsletterForm, SubscriptionForm, OrganizationForm
from inkmail.helpers import queue_message, queue_newsletter_message
from clubhouse.models import StaffMember
from website.models import Template, Page, Post, Resource, Link
from website.forms import TemplateForm, PageForm, PostForm, ResourceForm, LinkForm


@render_to("clubhouse/dashboard.html")
@login_required
def dashboard(request):
    page_name = "dashboard"
    return locals()


@login_required
def create_message(request):
    m = Message.objects.create()
    return redirect(reverse('clubhouse:message', kwargs={"hashid": m.hashid, }, host='clubhouse'))


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
    saved = False
    if request.method == "POST":
        form = MessageForm(request.POST, request.FILES, instance=message)
        if form.is_valid():
            form.save()
            saved = True
            message = Message.objects.get(hashid=hashid)
            form = MessageForm(instance=message)
    else:
        form = MessageForm(instance=message)
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


@render_to("clubhouse/subscriptions.html")
@login_required
def subscriptions(request):
    page_name = "subscriptions"
    subscriptions = Subscription.objects.all()
    return locals()


@render_to("clubhouse/subscription.html")
@login_required
def subscription(request, hashid):
    page_name = "subscriptions"
    s = Subscription.objects.get(hashid=hashid)
    return locals()


@render_to("clubhouse/newsletters.html")
@login_required
def newsletters(request):
    page_name = "newsletters"
    newsletters = Newsletter.objects.all()
    return locals()


@render_to("clubhouse/newsletter.html")
@login_required
def newsletter(request, hashid):
    page_name = "newsletters"
    saved = False
    n = Newsletter.objects.get(hashid=hashid)
    if request.method == "POST":
        form = NewsletterForm(request.POST, request.FILES, instance=n)
        if form.is_valid():
            form.save()
            saved = True
            n = Newsletter.objects.get(hashid=hashid)
            form = NewsletterForm(instance=n)
    else:
        form = NewsletterForm(instance=n)
    return locals()


@login_required
def create_newsletter(request):
    n = Newsletter.objects.create()
    return redirect(reverse('clubhouse:newsletter', kwargs={"hashid": n.hashid, }, host='clubhouse'))


@render_to("clubhouse/organization.html")
@login_required
def organization(request):
    page_name = "organization"
    o = Organization.get()
    if request.method == "POST":
        form = OrganizationForm(request.POST, request.FILES, instance=o)
        if form.is_valid():
            form.save()
            saved = True
            o = Organization.get()
            form = OrganizationForm(instance=o)
    else:
        form = OrganizationForm(instance=o)

    return locals()


@login_required
def create_scheduled_newsletter_message(request):
    snm = ScheduledNewsletterMessage.objects.create()
    return redirect(reverse('clubhouse:scheduled_newsletter_message', kwargs={"hashid": snm.hashid, }, host='clubhouse'))


@render_to("clubhouse/scheduled_newsletter_messages.html")
@login_required
def scheduled_newsletter_messages(request):
    page_name = "scheduled_newsletter_messages"
    scheduled_newsletter_messages = ScheduledNewsletterMessage.objects.all()
    return locals()


@render_to("clubhouse/scheduled_newsletter_message.html")
@login_required
def scheduled_newsletter_message(request, hashid):
    now = timezone.now()
    page_name = "scheduled_newsletter_messages"
    snm = ScheduledNewsletterMessage.objects.get(hashid=hashid)
    if request.method == "POST":
        form = ScheduledNewsletterMessageForm(request.POST, request.FILES, instance=snm)
        if form.is_valid():
            form.save()
            saved = True
            snm = ScheduledNewsletterMessage.objects.get(hashid=hashid)
            form = ScheduledNewsletterMessageForm(instance=snm)
    else:
        form = ScheduledNewsletterMessageForm(instance=snm)
    return locals()


@render_to("clubhouse/scheduled_newsletter_message_confirm_queue.html")
@login_required
def scheduled_newsletter_message_confirm_queue(request, hashid):
    page_name = "scheduled_newsletter_messages"
    snm = ScheduledNewsletterMessage.objects.get(hashid=hashid)
    return locals()


@render_to("clubhouse/scheduled_newsletter_message_queued.html")
@login_required
def scheduled_newsletter_message_queued(request, hashid):
    page_name = "scheduled_newsletter_messages"
    snm = ScheduledNewsletterMessage.objects.get(hashid=hashid)
    queue_newsletter_message.delay(snm.hashid)

    return locals()


@login_required
def create_template(request):
    t = Template.objects.create()
    return redirect(reverse('clubhouse:template', kwargs={"hashid": t.hashid, }, host='clubhouse'))


@render_to("clubhouse/templates.html")
@login_required
def templates(request):
    page_name = "templates"
    templates = Template.objects.all()
    return locals()


@render_to("clubhouse/template.html")
@login_required
def template(request, hashid):
    page_name = "templates"
    template = Template.objects.get(hashid=hashid)
    saved = False
    if request.method == "POST":
        form = TemplateForm(request.POST, request.FILES, instance=template)
        if form.is_valid():
            form.save()
            saved = True
            template = Template.objects.get(hashid=hashid)
            form = TemplateForm(instance=template)
    else:
        form = TemplateForm(instance=template)
    return locals()


@login_required
def create_page(request):
    p = Page.objects.create()
    return redirect(reverse('clubhouse:page', kwargs={"hashid": p.hashid, }, host='clubhouse'))


@render_to("clubhouse/pages.html")
@login_required
def pages(request):
    page_name = "pages"
    pages = Page.objects.all()
    return locals()


@render_to("clubhouse/page.html")
@login_required
def page(request, hashid):
    page_name = "pages"
    page = Page.objects.get(hashid=hashid)
    links = Link.objects.all()
    saved = False
    if request.method == "POST":
        form = PageForm(request.POST, request.FILES, instance=page)
        if form.is_valid():
            form.save()
            saved = True
            page = Page.objects.get(hashid=hashid)
            form = PageForm(instance=page)
    else:
        form = PageForm(instance=page)
    return locals()


@login_required
def create_post(request):
    p = Post.objects.create()
    return redirect(reverse('clubhouse:post', kwargs={"hashid": p.hashid, }, host='clubhouse'))


@render_to("clubhouse/posts.html")
@login_required
def posts(request):
    post_name = "posts"
    posts = Post.objects.all()
    return locals()


@render_to("clubhouse/post.html")
@login_required
def post(request, hashid):
    post_name = "posts"
    post = Post.objects.get(hashid=hashid)
    links = Link.objects.all()
    saved = False
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            saved = True
            post = Post.objects.get(hashid=hashid)
            form = PostForm(instance=post)
    else:
        form = PostForm(instance=post)
    return locals()


@login_required
def create_resource(request):
    p = Resource.objects.create()
    return redirect(reverse('clubhouse:resource', kwargs={"hashid": p.hashid, }, host='clubhouse'))


@render_to("clubhouse/resources.html")
@login_required
def resources(request):
    resource_name = "resources"
    resources = Resource.objects.all()
    return locals()


@render_to("clubhouse/resource.html")
@login_required
def resource(request, hashid):
    resource_name = "resources"
    resource = Resource.objects.get(hashid=hashid)
    saved = False
    if request.method == "POST":
        form = ResourceForm(request.POST, request.FILES, instance=resource)
        if form.is_valid():
            form.save()
            saved = True
            resource = Resource.objects.get(hashid=hashid)
            form = ResourceForm(instance=resource)
    else:
        form = ResourceForm(instance=resource)
    return locals()


@login_required
def create_link(request):
    print("create link")
    l = Link.objects.create()
    print(l)
    print(l.pk)

    return redirect(reverse('clubhouse:link', kwargs={"hashid": l.hashid, }, host='clubhouse'))


@render_to("clubhouse/links.html")
@login_required
def links(request):
    link_name = "links"
    links = Link.objects.all()
    return locals()


@render_to("clubhouse/link.html")
@login_required
def link(request, hashid):
    link_name = "links"
    link = Link.objects.get(hashid=hashid)
    saved = False
    if request.method == "POST":
        form = LinkForm(request.POST, request.FILES, instance=link)
        if form.is_valid():
            form.save()
            saved = True
            link = Link.objects.get(hashid=hashid)
            link.fetch_metadata_from_target()
            form = LinkForm(instance=link)
    else:
        form = LinkForm(instance=link)
    return locals()
