from base64 import b64decode
import datetime
import json
import logging
import time

from django.conf import settings
from django.core.mail import mail_admins
from django.contrib.auth import authenticate, login
from django.db import IntegrityError
from django.http import HttpResponse, Http404, HttpResponseNotModified
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.template import Context
from django.template import Template as DjangoTemplate
from django.template.response import TemplateResponse
from django.utils.html import mark_safe

from annoying.decorators import render_to, ajax_request
from utils.factory import Factory
from utils.helpers import reverse
from inkmail.models import Organization
from products.models import Product, ProductPurchase, Purchase, Journey, JourneyDay
from people.models import Person


@ajax_request
def check_login(request):
    if request.user.is_authenticated and not request.user.is_anonymous:
        return {
            "auth": True,
        }
    return {
        "auth": False,
    }


@render_to("products/home.html")
@login_required
def home(request):
    o = Organization.get()
    me = Person.objects.get(pk=request.user.pk)
    products = Product.objects.filter()
    return locals()


@render_to("products/productpurchase.html")
@login_required
def productpurchase(request, hashid):
    o = Organization.get()
    pp = ProductPurchase.objects.get(hashid=hashid)
    me = Person.objects.get(pk=request.user.pk)
    if pp.purchase.person != me:
        return redirect(reverse('logout'))

    return locals()


@render_to("products/start_journey.html")
@login_required
def start_journey(request, hashid):
    Organization.get()
    me = Person.objects.get(pk=request.user.pk)
    pp = ProductPurchase.objects.get(hashid=hashid)
    journey = Journey.objects.create(productpurchase=pp, start_date=timezone.now())
    if pp.purchase.person != me:
        return redirect(reverse('logout'))

    me = Person.objects.get(pk=request.user.pk)
    return redirect(reverse("products:journey", args=(journey.hashid,)))
    # return locals()


@render_to("products/journey.html")
@login_required
def journey(request, hashid):
    o = Organization.get()
    me = Person.objects.get(pk=request.user.pk)
    journey = Journey.objects.get(hashid=hashid)

    if journey.productpurchase.purchase.person != me:
        return redirect(reverse('logout'))

    # TODO: Add auth assertion
    return locals()


@render_to("products/confirm_delete_journey.html")
@login_required
def confirm_delete_journey(request, hashid):
    o = Organization.get()
    me = Person.objects.get(pk=request.user.pk)
    journey = Journey.objects.get(hashid=hashid)
    if journey.productpurchase.purchase.person != me:
        return redirect(reverse('logout'))

    return locals()


@login_required
@render_to("products/journey_deleted.html")
def delete_journey(request, hashid):
    o = Organization.get()
    me = Person.objects.get(pk=request.user.pk)
    try:
        journey = Journey.objects.get(hashid=hashid)
        if journey.productpurchase.purchase.person != me:
            return redirect(reverse('logout'))
        course_hashid = "%s" % journey.productpurchase.hashid
        journey.delete()
    except:
        pass

    return locals()


# @render_to("products/day.html")
@login_required
def day(request, hashid):
    consumer_str = Factory.rand_str(length=20, include_emoji=False)
    o = Organization.get()
    day = JourneyDay.objects.get(hashid=hashid)
    me = Person.objects.get(pk=request.user.pk)
    if day.journey.productpurchase.purchase.person != me:
        return redirect(reverse('logout'))

    data_store_url = "/ws/journey/%s/%s" % (
        day.journey.hashid,
        day.hashid,
    )
    person_store_url = "/ws/p/%s" % (
        me.hashid,
    )

    return TemplateResponse(
        request, 'products/%s/day-%s.html' % (
            day.journey.productpurchase.product.slug,
            day.day_number,
        ),
        locals()
    )


@render_to("products/today.html")
@login_required
def today(request):
    # TODO: Make this redirect to today's day.

    consumer_str = Factory.rand_str(length=20, include_emoji=False)
    if request.user.is_authenticated:
        me = Person.objects.get(pk=request.user.pk)
    else:
        return redirect(reverse('clubhouse:home'))

    date = datetime.datetime.today()

    return locals()
