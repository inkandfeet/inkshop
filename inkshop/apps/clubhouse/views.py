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
from utils.encryption import lookup_hash


@render_to("clubhouse/dashboard.html")
@login_required
def dashboard(request):
    o = Organization.get()
    page_name = "dashboard"
    return locals()


@login_required
def create_message(request):
    # o = Organization.get()
    m = Message.objects.create()
    return redirect(reverse('clubhouse:message', kwargs={"hashid": m.hashid, }, host='clubhouse'))


@render_to("clubhouse/messages.html")
@login_required
def messages(request):
    o = Organization.get()
    page_name = "messages"
    messages = Message.objects.all().order_by("-created_at")
    return locals()


@render_to("clubhouse/message.html")
@login_required
def message(request, hashid):
    o = Organization.get()
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
    o = Organization.get()
    page_name = "people"
    if request.method == "GET" and "q" in request.GET:
        hashed_email = lookup_hash(request.GET["q"])
        people = Person.objects.filter(hashed_email=lookup_hash)
    else:
        people = Person.objects.all()[:30]
    return locals()


@render_to("clubhouse/person.html")
@login_required
def person(request, hashid):
    o = Organization.get()
    page_name = "people"
    p = Person.objects.get(hashid=hashid)
    return locals()


@render_to("clubhouse/patrons.html")
@login_required
def patrons(request):
    o = Organization.get()
    page_name = "patrons"
    if request.method == "GET" and "q" in request.GET:
        hashed_email = lookup_hash(request.GET["q"])
        people = Person.objects.filter(hashed_email=lookup_hash, patron=True)
    elif request.method == "POST":
        adding = True
        added = False
        new_email = request.POST["patron_email"]
        new_patron = Person.get_by_email(new_email)
    
        if new_patron:
            added = True
            new_patron.patron = True
            new_patron.save()

        people = Person.objects.filter(patron=True).all()
    else:
        people = Person.objects.filter(patron=True).all()
    return locals()


@render_to("clubhouse/subscriptions.html")
@login_required
def subscriptions(request):
    o = Organization.get()
    page_name = "subscriptions"
    subscriptions = Subscription.objects.all()
    return locals()


@render_to("clubhouse/subscription.html")
@login_required
def subscription(request, hashid):
    o = Organization.get()
    page_name = "subscriptions"
    s = Subscription.objects.get(hashid=hashid)
    return locals()


@render_to("clubhouse/newsletters.html")
@login_required
def newsletters(request):
    o = Organization.get()
    page_name = "newsletters"
    newsletters = Newsletter.objects.all()
    return locals()


@render_to("clubhouse/newsletter.html")
@login_required
def newsletter(request, hashid):
    o = Organization.get()
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
    # o = Organization.get()
    n = Newsletter.objects.create()
    return redirect(reverse('clubhouse:newsletter', kwargs={"hashid": n.hashid, }, host='clubhouse'))


@render_to("clubhouse/organization.html")
@login_required
def organization(request):
    o = Organization.get()
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
    # o = Organization.get()
    snm = ScheduledNewsletterMessage.objects.create()
    return redirect(reverse('clubhouse:scheduled_newsletter_message', kwargs={"hashid": snm.hashid, }, host='clubhouse'))


@render_to("clubhouse/scheduled_newsletter_messages.html")
@login_required
def scheduled_newsletter_messages(request):
    o = Organization.get()
    page_name = "scheduled_newsletter_messages"
    scheduled_newsletter_messages = ScheduledNewsletterMessage.objects.all().order_by("-created_at")
    return locals()


@render_to("clubhouse/scheduled_newsletter_message.html")
@login_required
def scheduled_newsletter_message(request, hashid):
    o = Organization.get()
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
    o = Organization.get()
    page_name = "scheduled_newsletter_messages"
    snm = ScheduledNewsletterMessage.objects.get(hashid=hashid)
    return locals()


@render_to("clubhouse/scheduled_newsletter_message_queued.html")
@login_required
def scheduled_newsletter_message_queued(request, hashid):
    o = Organization.get()
    page_name = "scheduled_newsletter_messages"
    snm = ScheduledNewsletterMessage.objects.get(hashid=hashid)
    queue_newsletter_message.delay(snm.hashid)

    return locals()


@login_required
def create_template(request):
    # o = Organization.get()
    t = Template.objects.create()
    return redirect(reverse('clubhouse:template', kwargs={"hashid": t.hashid, }, host='clubhouse'))


@render_to("clubhouse/templates.html")
@login_required
def templates(request):
    o = Organization.get()
    page_name = "templates"
    templates = Template.objects.all()
    return locals()


@render_to("clubhouse/template.html")
@login_required
def template(request, hashid):
    o = Organization.get()
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


@render_to("clubhouse/template_delete.html")
@login_required
def delete_template(request, hashid):
    o = Organization.get()
    template = Template.objects.get(hashid=hashid)
    if request.method == "POST" and "delete" in request.POST and request.POST["delete"] == "DO_DELETE":
        template.delete()

        return redirect(reverse('clubhouse:templates', host='clubhouse'))
    return locals()


@login_required
def create_page(request):
    # o = Organization.get()
    p = Page.objects.create()
    return redirect(reverse('clubhouse:page', kwargs={"hashid": p.hashid, }, host='clubhouse'))


@render_to("clubhouse/pages.html")
@login_required
def pages(request):
    o = Organization.get()
    page_name = "pages"
    pages = Page.objects.all()
    return locals()


@render_to("clubhouse/page.html")
@login_required
def page(request, hashid):
    o = Organization.get()
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


@render_to("clubhouse/page_delete.html")
@login_required
def delete_page(request, hashid):
    o = Organization.get()
    page = Page.objects.get(hashid=hashid)
    if request.method == "POST" and "delete" in request.POST and request.POST["delete"] == "DO_DELETE":
        page.delete()

        return redirect(reverse('clubhouse:pages', host='clubhouse'))
    return locals()


@login_required
def create_post(request):
    # o = Organization.get()
    p = Post.objects.create()
    return redirect(reverse('clubhouse:post', kwargs={"hashid": p.hashid, }, host='clubhouse'))


@render_to("clubhouse/posts.html")
@login_required
def posts(request):
    o = Organization.get()
    post_name = "posts"
    posts = Post.objects.all()
    return locals()


@render_to("clubhouse/post.html")
@login_required
def post(request, hashid):
    o = Organization.get()
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


@render_to("clubhouse/post_delete.html")
@login_required
def delete_post(request, hashid):
    o = Organization.get()
    post = Post.objects.get(hashid=hashid)
    if request.method == "POST" and "delete" in request.POST and request.POST["delete"] == "DO_DELETE":
        post.delete()

        return redirect(reverse('clubhouse:posts', host='clubhouse'))
    return locals()


@login_required
def create_resource(request):
    # o = Organization.get()
    p = Resource.objects.create()
    return redirect(reverse('clubhouse:resource', kwargs={"hashid": p.hashid, }, host='clubhouse'))


@render_to("clubhouse/resources.html")
@login_required
def resources(request):
    o = Organization.get()
    resource_name = "resources"
    resources = Resource.objects.all()
    return locals()


@render_to("clubhouse/resource.html")
@login_required
def resource(request, hashid):
    o = Organization.get()
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


@render_to("clubhouse/resource_delete.html")
@login_required
def delete_resource(request, hashid):
    o = Organization.get()
    resource = Resource.objects.get(hashid=hashid)
    if request.method == "POST" and "delete" in request.POST and request.POST["delete"] == "DO_DELETE":
        resource.delete()

        return redirect(reverse('clubhouse:resources', host='clubhouse'))
    return locals()


@login_required
def create_link(request):
    # o = Organization.get()
    l = Link.objects.create()

    return redirect(reverse('clubhouse:link', kwargs={"hashid": l.hashid, }, host='clubhouse'))


@render_to("clubhouse/links.html")
@login_required
def links(request):
    o = Organization.get()
    link_name = "links"
    links = Link.objects.all()
    return locals()


@render_to("clubhouse/link.html")
@login_required
def link(request, hashid):
    o = Organization.get()
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


@render_to("clubhouse/link_delete.html")
@login_required
def delete_link(request, hashid):
    o = Organization.get()
    link = Link.objects.get(hashid=hashid)
    if request.method == "POST" and "delete" in request.POST and request.POST["delete"] == "DO_DELETE":
        link.delete()

        return redirect(reverse('clubhouse:links', host='clubhouse'))
    return locals()
