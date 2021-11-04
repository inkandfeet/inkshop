from base64 import b64decode
from decimal import Decimal
import datetime
import json
import os
import magic
import logging
import math
import random
import hashlib
import time

from django.core.cache import cache
from django.conf import settings
from django.core.mail import mail_admins
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.db import IntegrityError
from django.http import HttpResponse, Http404, HttpResponseNotModified, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, render_to_response
from django.template import Context

from django.template import Template as DjangoTemplate
from django.template.response import TemplateResponse
from django.utils.html import mark_safe
from ipware import get_client_ip

import stripe

from annoying.decorators import render_to, ajax_request
from utils.encryption import lookup_hash, encrypt, decrypt
from utils.factory import Factory
from utils.helpers import reverse, get_me
from inkmail.models import Organization
from products.models import Product, ProductPurchase, Purchase, Journey, JourneyDay, ProductFeedback
from products.models import BestimatorExperiment, BestimatorExperimentChoice, BestimatorAnswer
from people.models import Person

stripe.api_key = settings.STRIPE_SECRET_KEY
AD_GROUPS = {
    "sp": [
        "https://inkandfeet.com/sprint?s=gs7d10&spt=cDEw",  # $10
        "https://inkandfeet.com/sprint?s=gs7d2&spt=cDE5",   # $19
        "https://inkandfeet.com/sprint?s=gs7d3&spt=cDI5",   # $29
        "https://inkandfeet.com/sprint?s=gs7d4&spt=cDM5",   # $39
        "https://inkandfeet.com/sprint?s=gs7d5&spt=cDQ5",   # $49
        "https://inkandfeet.com/sprint?s=gs7d6&spt=cDU5",   # $59
        "https://inkandfeet.com/sprint?s=gs7d7&spt=cDY5",   # $69
        "https://inkandfeet.com/sprint?s=gs7d8&spt=cDc5",   # $79
        "https://inkandfeet.com/sprint?s=gs7d9&spt=cDg5",   # $89
    ]
}


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
    me = get_me(request)
    products = Product.objects.filter()
    if me.products.count() == 1:
        return redirect(reverse("products:productpurchase", args=(me.products.first().hashid, )))
    return locals()


def random_ad(request):
    try:
        group = AD_GROUPS[request.GET.get("g")]
    except:
        group = AD_GROUPS["sp"]
    return redirect(random.choice(group))


@ajax_request
def apple_app_site_association(request):
    return {
        "applinks": {
            "apps": [],
            "details": [
                # https://developer.apple.com/library/archive/documentation/General/Conceptual/AppSearch/UniversalLinks.html
                # {
                #     "appID": "9JA89QQLNQ.com.apple.wwdc",
                #     "paths": [ "/wwdc/news/", "/videos/wwdc/2015/*"]
                # },
                # {
                #     "appID": "ABCD1234.com.apple.wwdc",
                #     "paths": [ "*" ]
                # }
            ]
        }
    }


@render_to("products/account.html")
@login_required
def account(request):
    o = Organization.get()
    me = get_me(request)
    products = Product.objects.filter()
    information_updated = False
    password_changed = False

    if request.method == "POST":
        if request.POST.get("type") == "information":
            # Process info update
            me.first_name = request.POST["first_name"]
            me.email = request.POST["email"]
            me.turned_off_product_emails = request.POST.get("turned_off_product_emails", None) != "checked"
            me.save()
            information_updated = True

        elif request.POST.get("type") == "password":
            # Update password
            if request.POST.get("password"):
                password_message = "Password changed."
                me.set_password(request.POST["password"])
                me.save()
                update_session_auth_hash(request, me)
            else:
                password_message = "Password was blank."

    return locals()


@render_to("products/privacy.html")
def privacy(request):
    o = Organization.get()
    return locals()


@render_to("products/refund.html")
@login_required
def refund(request, hashid):
    o = Organization.get()
    me = get_me(request)
    pp = ProductPurchase.objects.get(hashid=hashid)

    return locals()


@render_to("products/refund_confirm.html")
@login_required
def refund_confirm(request, hashid):
    o = Organization.get()
    me = get_me(request)
    pp = ProductPurchase.objects.get(hashid=hashid)
    pp.purchase.refund(feedback=request.POST.get('feedback', None))

    return locals()


def course_purchase(request, course_slug):
    o = Organization.get()
    product = Product.get_from_slug(course_slug)
    purchased = False
    try:
        me = get_me(request)
        if me.products.filter(product=product).count() > 0:
            purchased = True
            pp = me.products.filter(product=product)[0]
            return redirect(reverse('products:productpurchase', args=(pp.hashid, )))
    except:
        pass
    # if not me and request.method == 'GET':
    #     cached_resp = cache.get("%s_purchase_not_logged_in%s" % (course_slug, request.META["QUERY_STRING"]))
    #     if cached_resp:
    #         return cached_resp
    #     else:
    #         resp = TemplateResponse(
    #             request, 'products/%s/purchase.html' % (
    #                 product.slug,
    #             ),
    #             locals()
    #         )
    #         resp.render()
    #         cache.set("%s_purchase_not_logged_in%s" % (course_slug, request.META["QUERY_STRING"]), resp)
    #         return resp

    resp = TemplateResponse(
        request, 'products/%s/purchase.html' % (
            product.slug,
        ),
        locals()
    )
    # resp.render()
    return resp


def course_beta_purchase(request, course_slug):
    o = Organization.get()
    product = Product.get_from_slug(course_slug)
    purchased = False
    try:
        me = get_me(request)
        if me.products.filter(product=product).count() > 0:
            purchased = True
            pp = me.products.filter(product=product)[0]
    except:
        pass
    return TemplateResponse(
        request, 'products/%s/purchase_beta.html' % (
            product.slug,
        ),
        locals()
    )


@csrf_exempt
@ajax_request
def create_account(request):
    data = {}
    if request.method == 'POST':
        data = json.loads(request.body)
        if request.user and request.user.is_authenticated and Person.objects.get(pk=request.user.pk):
            return {
                "success": True,
            }

        email = data["email"]
        if email:
            hashed_email = lookup_hash(email)
            password = data.get("password", None)
            first_name = data.get("first_name", None)
            p, created = Person.objects.get_or_create(hashed_email=hashed_email)
            if not created and p.password != 'Not Set' and p.password != '':
                valid_password = p.check_password(password)

                if not valid_password:
                    return {
                        "success": False,
                        "message": "That email exists, but the password doesn't match."
                    }
                else:
                    if first_name:
                        p.first_name = first_name

                    p.save()
                    login(request, p)

            else:
                p.email = email
                if first_name:
                    p.first_name = first_name
                if password:
                    p.set_password(password)
                p.save()
                login(request, p)

            return {
                "success": True,
            }

    if "email" not in data or not data["email"]:
        message = "Please enter your email address, so we can send the book somewhere. :)"

    else:
        message = "%s%s" % (
            "Hm. We ran into an error creating your account.  Please try again in a minute,",
            " and if it still doesn't work please email me at steven@inkandfeet.com!"
        )

    return {
        "message": message,
        "success": False,
    }


@csrf_exempt
@ajax_request
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return stripe_config


@csrf_exempt
@ajax_request
def create_checkout_session(request, course_slug):
    product = Product.get_from_slug(course_slug)
    try:
        me = get_me(request)
        if request.method == 'GET':
            beta = request.GET.get('beta') == "yesplease"
            help_edition = request.GET.get('he') == "1"
            help_edition_price = request.GET.get('p')
            if help_edition and not help_edition_price:
                message = "%s" % (
                    "Please enter a price.  For no cost, put in 0.",
                )
                return {'error': message}
            test_price = request.GET.get('t')
            try:
                test_price = int(b64decode(test_price)[1:])
                if test_price <= 0:
                    test_price = None
            except:
                pass

            host = request.META["HTTP_HOST"]
            domain_url = 'https://%s%s' % (host, reverse('products:course_purchase', args=(product.slug,)))

            price = product.stripe_price_id
            # mode = 'payment'
            price_data = None
            if beta:
                price = product.stripe_beta_price_id
            if test_price:
                price = "%s00" % test_price
                price_data = {
                    "unit_amount": price,
                    "currency": "usd",
                    "product": product.stripe_product_id,
                }
                line_items = [
                    {
                        # 'name': '7-Day Sprint',
                        'quantity': 1,
                        # 'currency': 'usd',
                        # 'amount': '10000',
                        'price_data': price_data,
                    }
                ]
            elif help_edition:
                price = int(help_edition_price.replace(".", ""))
                price_data = {
                    "unit_amount": price,
                    "currency": "usd",
                    "product": product.stripe_product_id,
                }
                line_items = [
                    {
                        # 'name': '7-Day Sprint',
                        'quantity': 1,
                        # 'currency': 'usd',
                        # 'amount': '10000',
                        'price_data': price_data,
                    }
                ]
            else:
                line_items = [
                    {
                        # 'name': '7-Day Sprint',
                        'quantity': 1,
                        # 'currency': 'usd',
                        # 'amount': '10000',
                        'price': price,
                    }
                ]

                # mode = 'subscription'
            # print(price)

            try:
                # Create new Checkout Session for the order
                # Other optional params include:
                # [billing_address_collection] - to display billing address details on the page
                # [customer] - if you have an existing Stripe Customer ID
                # [payment_intent_data] - capture the payment later
                # [customer_email] - prefill the email input in the form
                # For full details see https://stripe.com/docs/api/checkout/sessions/create

                # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
                client_reference_id = "%s.%s" % (me.hashid, product.hashid)
                checkout_session = stripe.checkout.Session.create(
                    # submit_type='donate',
                    client_reference_id=client_reference_id,
                    customer_email=me.email,
                    success_url=domain_url + '/purchase/success?session_id={CHECKOUT_SESSION_ID}&ci=%s' % me.hashid,
                    cancel_url=domain_url + '/purchase/cancelled',
                    payment_method_types=['card'],
                    mode='payment',
                    allow_promotion_codes=True,
                    line_items=line_items,
                )
                return {'sessionId': checkout_session['id']}
            except Exception as e:
                return {'error': str(e)}
    except:
        message = "%s%s%s" % (
            "Hm. We ran into an error creating your account.  Please check that you've entered a valid email above,",
            " and if it still doesn't work please email me at steven@inkandfeet.com so I can find this bug, and",
            " get you sorted out!"
        )
        return {'error': message}


@login_required
def checkout_success(request, course_slug):
    o = Organization.get()
    product = Product.get_from_slug(course_slug)
    p = Person.objects.get(hashid=request.GET['ci'])
    me = get_me(request)
    sess = stripe.checkout.Session.retrieve(request.GET['session_id'])
    # print(sess)
    assert p == me
    purchase, purchase_created = Purchase.objects.get_or_create(
        person=p,
        stripe_session_id=sess["id"],
        stripe_payment_intent_id=sess["payment_intent"],
    )
    purchase.total = Decimal(sess["amount_total"] / 100)
    purchase.save()
    pp, pp_created = ProductPurchase.objects.get_or_create(
        product=product,
        purchase=purchase,
    )
    pp.send_purchase_email()
    # pp = ProductPurchase.objects.get(hashid=hashid)
    # if pp.purchase.person != me:
    #     return redirect(reverse('logout'))

    return TemplateResponse(
        request, 'products/%s/checkout_success.html' % (
            product.slug,
        ),
        locals()
    )


# @ajax_request
@csrf_exempt
def checkout_help_edition(request, course_slug):
    o = Organization.get()
    product = Product.get_from_slug(course_slug)
    try:
        me = get_me(request)
    except:
        return redirect("%s?help_edition=1" % reverse("products:course_purchase", args=(product.slug,)))

    purchase, purchase_created = Purchase.objects.get_or_create(
        person=me,
        help_edition=True,
    )
    purchase.total = Decimal(0.00)
    purchase.save()
    pp, pp_created = ProductPurchase.objects.get_or_create(
        product=product,
        purchase=purchase,
    )
    pp.send_purchase_email()
    # pp = ProductPurchase.objects.get(hashid=hashid)
    # if pp.purchase.person != me:
    #     return redirect(reverse('logout'))

    return TemplateResponse(
        request, 'products/%s/checkout_success.html' % (
            product.slug,
        ),
        locals()
    )


@login_required
def purchase_complete(request, course_slug):
    try:
        o = Organization.get()
        product = Product.get_from_slug(course_slug)
        me = get_me(request)

        pp = ProductPurchase.objects.filter(
            product=product,
            purchase__person=me,
            purchase__refunded=False,
        ).all().first()

        return TemplateResponse(
            request, 'products/%s/checkout_success.html' % (
                product.slug,
            ),
            locals()
        )
    except:
        return redirect(reverse('login'))


@login_required
def product_download(request, course_slug, resource_url):
    try:
        product = Product.get_from_slug(course_slug)
        me = get_me(request)

        if ProductPurchase.objects.filter(
            product=product,
            purchase__person=me,
            purchase__refunded=False,
        ).all().count() > 0:
            view_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
            with open(os.path.join(view_dir, "products", "downloads", course_slug, resource_url), "rb") as f:
                content = f.read()

            mime_type = magic.from_buffer(content, mime=True)
            response = HttpResponse(content, content_type=mime_type)
            response['Content-Type'] = mime_type
            response['Content-Length'] = len(content)
            return response

        return redirect(reverse('login'))
    except:
        import traceback
        traceback.print_exc()
        return redirect(reverse('login'))


@login_required
def checkout_cancelled(request, course_slug):
    o = Organization.get()
    product = Product.get_from_slug(course_slug)
    # pp = ProductPurchase.objects.get(hashid=hashid)
    # me = get_me(request)
    # if pp.purchase.person != me:
    #     return redirect(reverse('logout'))

    return TemplateResponse(
        request, 'products/%s/checkout_cancelled.html' % (
            product.slug,
        ),
        locals()
    )


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        # Invalid payload
        return HttpResponse(status=200)
        # return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return HttpResponse(status=200)
        # return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        print("Payment was successful.")

        # stripe_payment_confirmed
        person_hashid, product_hashid = event["data"]["object"]["client_reference_id"].split(".")
        p = Person.objects.get(hashid=person_hashid)
        sess = stripe.checkout.Session.retrieve(event["data"]["object"]["id"])
        assert sess["id"] == event["data"]["object"]["id"]
        product = Product.objects.get(hashid=product_hashid)
        purchase, purchase_created = Purchase.objects.get_or_create(
            person=p,
            stripe_session_id=event["data"]["object"]["id"],
        )
        purchase.total = Decimal(event["data"]["object"]["amount_total"] / 100)
        purchase.stripe_payment_confirmed = True
        purchase.stripe_payment_confirmed_at = timezone.now()
        purchase.save()

        pp, pp_created = ProductPurchase.objects.get_or_create(
            product=product,
            purchase=purchase,
        )

    return HttpResponse(status=200)


@render_to("products/productpurchase.html")
@login_required
def productpurchase(request, hashid):
    o = Organization.get()
    pp = ProductPurchase.objects.get(hashid=hashid)
    me = get_me(request)
    if pp.purchase.person != me:
        return redirect(reverse('logout'))

    purchase = pp.purchase
    product = pp.product
    post_purchase = True
    if product.is_downloadable:
        return TemplateResponse(
            request, 'products/%s/checkout_success.html' % (
                product.slug,
            ),
            locals()
        )

    return locals()


@render_to("products/start_journey.html")
@login_required
def start_journey(request, hashid):
    Organization.get()
    me = get_me(request)
    pp = ProductPurchase.objects.get(hashid=hashid)
    Journey.objects.create(productpurchase=pp, start_date=timezone.now())
    if pp.purchase.person != me:
        return redirect(reverse('logout'))

    me = get_me(request)
    return redirect(reverse("products:productpurchase", args=(pp.hashid,)))
    # return locals()


@render_to("products/journey.html")
@login_required
def journey(request, hashid):
    o = Organization.get()
    me = get_me(request)
    journey = Journey.objects.get(hashid=hashid)

    if journey.productpurchase.purchase.person != me:
        return redirect(reverse('logout'))

    # TODO: Add auth assertion
    return locals()


@render_to("products/confirm_delete_journey.html")
@login_required
def confirm_delete_journey(request, hashid):
    o = Organization.get()
    me = get_me(request)
    journey = Journey.objects.get(hashid=hashid)
    if journey.productpurchase.purchase.person != me:
        return redirect(reverse('logout'))

    return locals()


@login_required
@render_to("products/journey_deleted.html")
def delete_journey(request, hashid):
    o = Organization.get()
    me = get_me(request)
    try:
        journey = Journey.objects.get(hashid=hashid)
        pp_hashid = journey.productpurchase.hashid
        assert request.method == "POST"
        assert request.POST.get("do_delete") == "yes"
        if journey.productpurchase.purchase.person != me:
            return redirect(reverse('logout'))
        course_hashid = "%s" % journey.productpurchase.hashid
        journey.delete()
        return redirect(reverse('products:productpurchase', args=(pp_hashid, )))
    except:
        return redirect(reverse('products:home'))
        pass

    return locals()


# @render_to("products/day.html")
@login_required
def day(request, hashid):
    consumer_str = Factory.rand_str(length=20, include_emoji=False)
    o = Organization.get()
    day = JourneyDay.objects.get(hashid=hashid)
    me = get_me(request)
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
        me = get_me(request)
    else:
        return redirect(reverse('clubhouse:home'))

    date = datetime.datetime.today()

    return locals()


def data_export(request):
    me = get_me(request)

    return JsonResponse(me.gdpr_dump, content_type='application/json', json_dumps_params={'indent': 4})


@render_to("products/confirm_delete_account.html")
@login_required
def confirm_delete_account(request):
    o = Organization.get()
    me = get_me(request)

    if request.POST.get("submit") == "yes":
        me.delete()
        user = request.user
        logout(request)
        user.delete()
        return redirect(reverse('products:account_deleted'))

    return locals()


@render_to("products/account_deleted.html")
def account_deleted(request):
    return locals()


@ajax_request
@csrf_exempt
def send_feedback(request, course_slug):
    product = Product.get_from_slug(course_slug)
    me = get_me(request)
    ProductFeedback.objects.create(
        product=product,
        person=me,
        raw_data=json.dumps(json.loads(request.body)),
    )
    return {
        "suceess": True,
    }


@render_to("products/bestimator/bestimator.html")
def bestimator(request):
    # TODO: Make this redirect to bestimator's day.

    date = datetime.datetime.today()
    experiments = BestimatorExperiment.objects.all()

    return locals()


@render_to("products/bestimator/bestimator_experiment.html")
def bestimator_experiment(request, slug):
    if "bestid" not in request.GET:
        now = timezone.now()
        bestid = "%s%s" % (
            now.time(),
            Factory.rand_str(length=10, include_emoji=False)
        )
        bestid = bestid.encode('utf-8').hex()
        return redirect("%s?bestid=%s" % (
            reverse("products:bestimator_experiment", args=(slug, )),
            bestid,
        ))
    else:
        bestid = request.GET["bestid"]

    date = datetime.datetime.today()
    experiment = BestimatorExperiment.objects.get(slug=slug)

    answer_objs = BestimatorAnswer.objects.filter(
        experiment_choice__experiment=experiment,
        session_hash=bestid,
    )
    if answer_objs.count() > 0:
        answers = {}
        for a in answer_objs:
            answers[a.experiment_choice.slug] = a

    return locals()


@ajax_request
@csrf_exempt
def bestimator_save_feedback(request, slug):
    try:
        experiment = BestimatorExperiment.objects.get(slug=slug)
        if request.method == "POST":
            data = json.loads(request.body)
            for slug, choice_answers in data["choices"].items():
                choice = BestimatorExperimentChoice.objects.get(experiment=experiment, slug=slug)
                answer, _ = BestimatorAnswer.objects.get_or_create(
                    session_hash=data["feedback_session"],
                    experiment_choice=choice,
                )
                for k, v in choice_answers.items():
                    if choice_answers[k] is not None:
                        answer.__dict__[k] = v
                answer.save()

        return {
            "suceess": True,
        }
    except Exception as e:
        raise e
        return {
            "suceess": False,
        }


def one_click_sign_in(request, link):
    # print(link)
    try:
        # print(decrypt(link))
        _, user_hashid, url = decrypt(link).split("|")
        me = Person.objects.get(hashid=user_hashid)
        update_session_auth_hash(request, me)
        login(request, me)
        return redirect(url)
    except:
        return redirect(reverse('login'))


def course_link_redirect(request, url):
    return redirect("/%s" % url)
