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
from django.contrib.admin.views.decorators import staff_member_required
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
from products.models import Product, ProductPurchase, Purchase, Journey, ProductDay
from products.models import BestimatorExperiment, BestimatorExperimentChoice
from products.forms import ProductForm, ProductPurchaseForm, PurchaseForm, JourneyForm, ProductDayForm
from products.forms import BestimatorExperimentForm, BestimatorExperimentChoiceForm
from clubhouse.models import StaffMember
from website.models import Template, Page, Post, Resource, Link
from website.forms import TemplateForm, PageForm, PostForm, ResourceForm, LinkForm
from utils.encryption import lookup_hash


@render_to("clubhouse/dashboard.html")
@staff_member_required(login_url='login')
def dashboard(request):
    o = Organization.get()
    page_name = "dashboard"
    return locals()


@staff_member_required(login_url='login')
def create_message(request):
    # o = Organization.get()
    m = Message.objects.create()
    return redirect(reverse('clubhouse:message', kwargs={"hashid": m.hashid, }, host='clubhouse'))


@render_to("clubhouse/messages.html")
@staff_member_required(login_url='login')
def messages(request):
    o = Organization.get()
    page_name = "messages"
    messages = Message.objects.all().order_by("-created_at")
    return locals()


@render_to("clubhouse/message.html")
@staff_member_required(login_url='login')
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
@staff_member_required(login_url='login')
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
@staff_member_required(login_url='login')
def person(request, hashid):
    o = Organization.get()
    page_name = "people"
    p = Person.objects.get(hashid=hashid)
    return locals()


@render_to("clubhouse/patrons.html")
@staff_member_required(login_url='login')
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
@staff_member_required(login_url='login')
def subscriptions(request):
    o = Organization.get()
    page_name = "subscriptions"
    subscriptions = Subscription.objects.all()
    return locals()


@render_to("clubhouse/subscription.html")
@staff_member_required(login_url='login')
def subscription(request, hashid):
    o = Organization.get()
    page_name = "subscriptions"
    s = Subscription.objects.get(hashid=hashid)
    return locals()


@render_to("clubhouse/newsletters.html")
@staff_member_required(login_url='login')
def newsletters(request):
    o = Organization.get()
    page_name = "newsletters"
    newsletters = Newsletter.objects.all()
    return locals()


@render_to("clubhouse/newsletter.html")
@staff_member_required(login_url='login')
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


@staff_member_required(login_url='login')
def create_newsletter(request):
    # o = Organization.get()
    n = Newsletter.objects.create()
    return redirect(reverse('clubhouse:newsletter', kwargs={"hashid": n.hashid, }, host='clubhouse'))


@render_to("clubhouse/organization.html")
@staff_member_required(login_url='login')
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


@staff_member_required(login_url='login')
def create_scheduled_newsletter_message(request):
    # o = Organization.get()
    snm = ScheduledNewsletterMessage.objects.create()
    return redirect(reverse('clubhouse:scheduled_newsletter_message', kwargs={"hashid": snm.hashid, }, host='clubhouse'))


@render_to("clubhouse/scheduled_newsletter_messages.html")
@staff_member_required(login_url='login')
def scheduled_newsletter_messages(request):
    o = Organization.get()
    page_name = "scheduled_newsletter_messages"
    scheduled_newsletter_messages = ScheduledNewsletterMessage.objects.all().order_by("-created_at")
    return locals()


@render_to("clubhouse/scheduled_newsletter_message.html")
@staff_member_required(login_url='login')
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
@staff_member_required(login_url='login')
def scheduled_newsletter_message_confirm_queue(request, hashid):
    o = Organization.get()
    page_name = "scheduled_newsletter_messages"
    snm = ScheduledNewsletterMessage.objects.get(hashid=hashid)
    return locals()


@render_to("clubhouse/scheduled_newsletter_message_queued.html")
@staff_member_required(login_url='login')
def scheduled_newsletter_message_queued(request, hashid):
    o = Organization.get()
    page_name = "scheduled_newsletter_messages"
    snm = ScheduledNewsletterMessage.objects.get(hashid=hashid)
    queue_newsletter_message.delay(snm.hashid)

    return locals()


@staff_member_required(login_url='login')
def create_template(request):
    # o = Organization.get()
    t = Template.objects.create()
    return redirect(reverse('clubhouse:template', kwargs={"hashid": t.hashid, }, host='clubhouse'))


@render_to("clubhouse/templates.html")
@staff_member_required(login_url='login')
def templates(request):
    o = Organization.get()
    page_name = "templates"
    templates = Template.objects.all()
    return locals()


@render_to("clubhouse/template.html")
@staff_member_required(login_url='login')
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
@staff_member_required(login_url='login')
def delete_template(request, hashid):
    o = Organization.get()
    template = Template.objects.get(hashid=hashid)
    if request.method == "POST" and "delete" in request.POST and request.POST["delete"] == "DO_DELETE":
        template.delete()

        return redirect(reverse('clubhouse:templates', host='clubhouse'))
    return locals()


@staff_member_required(login_url='login')
def create_page(request):
    # o = Organization.get()
    p = Page.objects.create()
    return redirect(reverse('clubhouse:page', kwargs={"hashid": p.hashid, }, host='clubhouse'))


@render_to("clubhouse/pages.html")
@staff_member_required(login_url='login')
def pages(request):
    o = Organization.get()
    page_name = "pages"
    pages = Page.objects.all()
    return locals()


@render_to("clubhouse/page.html")
@staff_member_required(login_url='login')
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
@staff_member_required(login_url='login')
def delete_page(request, hashid):
    o = Organization.get()
    page = Page.objects.get(hashid=hashid)
    if request.method == "POST" and "delete" in request.POST and request.POST["delete"] == "DO_DELETE":
        page.delete()

        return redirect(reverse('clubhouse:pages', host='clubhouse'))
    return locals()


@staff_member_required(login_url='login')
def create_post(request):
    # o = Organization.get()
    p = Post.objects.create()
    return redirect(reverse('clubhouse:post', kwargs={"hashid": p.hashid, }, host='clubhouse'))


@render_to("clubhouse/posts.html")
@staff_member_required(login_url='login')
def posts(request):
    o = Organization.get()
    page_name = "posts"
    posts = Post.objects.all()
    return locals()


@render_to("clubhouse/post.html")
@staff_member_required(login_url='login')
def post(request, hashid):
    o = Organization.get()
    page_name = "posts"
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
@staff_member_required(login_url='login')
def delete_post(request, hashid):
    o = Organization.get()
    post = Post.objects.get(hashid=hashid)
    if request.method == "POST" and "delete" in request.POST and request.POST["delete"] == "DO_DELETE":
        post.delete()

        return redirect(reverse('clubhouse:posts', host='clubhouse'))
    return locals()


@staff_member_required(login_url='login')
def create_resource(request):
    # o = Organization.get()
    p = Resource.objects.create()
    return redirect(reverse('clubhouse:resource', kwargs={"hashid": p.hashid, }, host='clubhouse'))


@render_to("clubhouse/resources.html")
@staff_member_required(login_url='login')
def resources(request):
    o = Organization.get()
    page_name = "resources"
    resources = Resource.objects.all()
    return locals()


@render_to("clubhouse/resource.html")
@staff_member_required(login_url='login')
def resource(request, hashid):
    o = Organization.get()
    page_name = "resources"
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
@staff_member_required(login_url='login')
def delete_resource(request, hashid):
    o = Organization.get()
    resource = Resource.objects.get(hashid=hashid)
    if request.method == "POST" and "delete" in request.POST and request.POST["delete"] == "DO_DELETE":
        resource.delete()

        return redirect(reverse('clubhouse:resources', host='clubhouse'))
    return locals()


@staff_member_required(login_url='login')
def create_link(request):
    # o = Organization.get()
    l = Link.objects.create()

    return redirect(reverse('clubhouse:link', kwargs={"hashid": l.hashid, }, host='clubhouse'))


@render_to("clubhouse/links.html")
@staff_member_required(login_url='login')
def links(request):
    o = Organization.get()
    page_name = "links"
    links = Link.objects.all()
    return locals()


@render_to("clubhouse/link.html")
@staff_member_required(login_url='login')
def link(request, hashid):
    o = Organization.get()
    page_name = "links"
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
@staff_member_required(login_url='login')
def delete_link(request, hashid):
    o = Organization.get()
    link = Link.objects.get(hashid=hashid)
    if request.method == "POST" and "delete" in request.POST and request.POST["delete"] == "DO_DELETE":
        link.delete()

        return redirect(reverse('clubhouse:links', host='clubhouse'))
    return locals()


@staff_member_required(login_url='login')
def create_product(request):
    # o = Organization.get()
    p = Product.objects.create()
    return redirect(reverse('clubhouse:product', kwargs={"hashid": p.hashid, }, host='clubhouse'))


@render_to("clubhouse/products.html")
@staff_member_required(login_url='login')
def products(request):
    o = Organization.get()
    page_name = "products"
    products = Product.objects.all()
    return locals()


@render_to("clubhouse/product.html")
@staff_member_required(login_url='login')
def product(request, hashid):
    o = Organization.get()
    page_name = "products"
    product = Product.objects.get(hashid=hashid)
    links = Link.objects.all()
    saved = False
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            saved = True
            product = Product.objects.get(hashid=hashid)
            form = ProductForm(instance=product)
    else:
        form = ProductForm(instance=product)
    return locals()


@render_to("clubhouse/product_delete.html")
@staff_member_required(login_url='login')
def delete_product(request, hashid):
    o = Organization.get()
    product = Product.objects.get(hashid=hashid)
    if request.method == "POST" and "delete" in request.POST and request.POST["delete"] == "DO_DELETE":
        product.delete()

        return redirect(reverse('clubhouse:products', host='clubhouse'))
    return locals()


@staff_member_required(login_url='login')
def create_productpurchase(request):
    # o = Organization.get()
    p = ProductPurchase.objects.create()
    return redirect(reverse('clubhouse:productpurchase', kwargs={"hashid": p.hashid, }, host='clubhouse'))


@render_to("clubhouse/productpurchases.html")
@staff_member_required(login_url='login')
def productpurchases(request):
    o = Organization.get()
    page_name = "productpurchases"
    productpurchases = ProductPurchase.objects.all().order_by("-created_at")
    return locals()


@render_to("clubhouse/productpurchase.html")
@staff_member_required(login_url='login')
def productpurchase(request, hashid):
    o = Organization.get()
    page_name = "productpurchases"
    productpurchase = ProductPurchase.objects.get(hashid=hashid)
    links = Link.objects.all()
    saved = False
    if request.method == "POST":
        form = ProductPurchaseForm(request.POST, request.FILES, instance=productpurchase)
        if form.is_valid():
            form.save()
            saved = True
            productpurchase = ProductPurchase.objects.get(hashid=hashid)
            form = ProductPurchaseForm(instance=productpurchase)
    else:
        form = ProductPurchaseForm(instance=productpurchase)
    return locals()


@render_to("clubhouse/productpurchase_delete.html")
@staff_member_required(login_url='login')
def delete_productpurchase(request, hashid):
    o = Organization.get()
    productpurchase = ProductPurchase.objects.get(hashid=hashid)
    if request.method == "POST" and "delete" in request.POST and request.POST["delete"] == "DO_DELETE":
        productpurchase.delete()

        return redirect(reverse('clubhouse:productpurchases', host='clubhouse'))
    return locals()


@staff_member_required(login_url='login')
def create_purchase(request):
    # o = Organization.get()
    p = Purchase.objects.create()
    return redirect(reverse('clubhouse:purchase', kwargs={"hashid": p.hashid, }, host='clubhouse'))


@render_to("clubhouse/purchases.html")
@staff_member_required(login_url='login')
def purchases(request):
    o = Organization.get()
    page_name = "purchases"
    purchases = Purchase.objects.all().order_by("-created_at")
    return locals()


@render_to("clubhouse/purchase.html")
@staff_member_required(login_url='login')
def purchase(request, hashid):
    o = Organization.get()
    page_name = "purchases"
    purchase = Purchase.objects.get(hashid=hashid)
    links = Link.objects.all()
    saved = False
    if request.method == "POST":
        form = PurchaseForm(request.POST, request.FILES, instance=purchase)
        if form.is_valid():
            form.save()
            saved = True
            purchase = Purchase.objects.get(hashid=hashid)
            form = PurchaseForm(instance=purchase)
    else:
        form = PurchaseForm(instance=purchase)
    return locals()


@render_to("clubhouse/purchase_delete.html")
@staff_member_required(login_url='login')
def delete_purchase(request, hashid):
    o = Organization.get()
    purchase = Purchase.objects.get(hashid=hashid)
    if request.method == "POST" and "delete" in request.POST and request.POST["delete"] == "DO_DELETE":
        purchase.delete()

        return redirect(reverse('clubhouse:purchases', host='clubhouse'))
    return locals()


@staff_member_required(login_url='login')
def create_journey(request):
    # o = Organization.get()
    p = Journey.objects.create()
    return redirect(reverse('clubhouse:journey', kwargs={"hashid": p.hashid, }, host='clubhouse'))


@render_to("clubhouse/journeys.html")
@staff_member_required(login_url='login')
def journeys(request):
    o = Organization.get()
    page_name = "journeys"
    journeys = Journey.objects.all()
    return locals()


@render_to("clubhouse/journey.html")
@staff_member_required(login_url='login')
def journey(request, hashid):
    o = Organization.get()
    page_name = "journeys"
    journey = Journey.objects.get(hashid=hashid)
    links = Link.objects.all()
    saved = False
    if request.method == "POST":
        form = JourneyForm(request.POST, request.FILES, instance=journey)
        if form.is_valid():
            form.save()
            saved = True
            journey = Journey.objects.get(hashid=hashid)
            form = JourneyForm(instance=journey)
    else:
        form = JourneyForm(instance=journey)
    return locals()


@render_to("clubhouse/journey_delete.html")
@staff_member_required(login_url='login')
def delete_journey(request, hashid):
    o = Organization.get()
    journey = Journey.objects.get(hashid=hashid)
    if request.method == "POST" and "delete" in request.POST and request.POST["delete"] == "DO_DELETE":
        journey.delete()

        return redirect(reverse('clubhouse:journeys', host='clubhouse'))
    return locals()


@staff_member_required(login_url='login')
def create_productday(request):
    # o = Organization.get()
    p = ProductDay.objects.create()
    return redirect(reverse('clubhouse:productday', kwargs={"hashid": p.hashid, }, host='clubhouse'))


@render_to("clubhouse/productdays.html")
@staff_member_required(login_url='login')
def productdays(request):
    o = Organization.get()
    page_name = "productdays"
    productdays = ProductDay.objects.all()
    return locals()


@render_to("clubhouse/productday.html")
@staff_member_required(login_url='login')
def productday(request, hashid):
    o = Organization.get()
    page_name = "productdays"
    productday = ProductDay.objects.get(hashid=hashid)
    links = Link.objects.all()
    saved = False
    if request.method == "POST":
        form = ProductDayForm(request.POST, request.FILES, instance=productday)
        if form.is_valid():
            form.save()
            saved = True
            productday = ProductDay.objects.get(hashid=hashid)
            form = ProductDayForm(instance=productday)
    else:
        form = ProductDayForm(instance=productday)
    return locals()


@render_to("clubhouse/productday_delete.html")
@staff_member_required(login_url='login')
def delete_productday(request, hashid):
    o = Organization.get()
    productday = ProductDay.objects.get(hashid=hashid)
    if request.method == "POST" and "delete" in request.POST and request.POST["delete"] == "DO_DELETE":
        productday.delete()

        return redirect(reverse('clubhouse:productdays', host='clubhouse'))
    return locals()


@staff_member_required(login_url='login')
def create_bestimator(request):
    # o = Organization.get()
    p = BestimatorExperiment.objects.create()
    return redirect(reverse('clubhouse:bestimator', kwargs={"hashid": p.hashid, }, host='clubhouse'))


@render_to("clubhouse/bestimators.html")
@staff_member_required(login_url='login')
def bestimators(request):
    o = Organization.get()
    page_name = "bestimators"
    bestimators = BestimatorExperiment.objects.all()
    return locals()


@render_to("clubhouse/bestimator.html")
@staff_member_required(login_url='login')
def bestimator(request, hashid):
    o = Organization.get()
    page_name = "bestimators"
    bestimator = BestimatorExperiment.objects.get(hashid=hashid)
    saved = False
    if request.method == "POST":
        form = BestimatorExperimentForm(request.POST, request.FILES, instance=bestimator)
        if form.is_valid():
            form.save()
            saved = True
            bestimator = BestimatorExperiment.objects.get(hashid=hashid)
            form = BestimatorExperimentForm(instance=bestimator)
    else:
        form = BestimatorExperimentForm(instance=bestimator)
    return locals()


@render_to("clubhouse/bestimator_delete.html")
@staff_member_required(login_url='login')
def delete_bestimator(request, hashid):
    o = Organization.get()
    bestimator = BestimatorExperiment.objects.get(hashid=hashid)
    if request.method == "POST" and "delete" in request.POST and request.POST["delete"] == "DO_DELETE":
        bestimator.delete()

        return redirect(reverse('clubhouse:bestimators', host='clubhouse'))
    return locals()


@staff_member_required(login_url='login')
def create_bestimator_choice(request):
    # o = Organization.get()
    p = BestimatorExperimentChoice.objects.create()
    return redirect(reverse('clubhouse:bestimator_choice', kwargs={"hashid": p.hashid, }, host='clubhouse'))


@render_to("clubhouse/bestimator_choices.html")
@staff_member_required(login_url='login')
def bestimator_choices(request):
    o = Organization.get()
    page_name = "bestimator_choices"
    bestimator_choices = BestimatorExperimentChoice.objects.all()
    return locals()


@render_to("clubhouse/bestimator_choice.html")
@staff_member_required(login_url='login')
def bestimator_choice(request, hashid):
    o = Organization.get()
    page_name = "bestimator_choices"
    bestimator_choice = BestimatorExperimentChoice.objects.get(hashid=hashid)
    links = Link.objects.all()
    saved = False
    if request.method == "POST":
        form = BestimatorExperimentChoiceForm(request.POST, request.FILES, instance=bestimator_choice)
        if form.is_valid():
            form.save()
            saved = True
            bestimator_choice = BestimatorExperimentChoice.objects.get(hashid=hashid)
            form = BestimatorExperimentChoiceForm(instance=bestimator_choice)
    else:
        form = BestimatorExperimentChoiceForm(instance=bestimator_choice)
    return locals()


@render_to("clubhouse/bestimator_choice_delete.html")
@staff_member_required(login_url='login')
def delete_bestimator_choice(request, hashid):
    o = Organization.get()
    bestimator_choice = BestimatorExperimentChoice.objects.get(hashid=hashid)
    if request.method == "POST" and "delete" in request.POST and request.POST["delete"] == "DO_DELETE":
        bestimator_choice.delete()

        return redirect(reverse('clubhouse:bestimator_choices', host='clubhouse'))
    return locals()
