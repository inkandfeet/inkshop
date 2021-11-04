import datetime
import json
import logging
import requests

from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail as django_send_mail
from celery.task import task, periodic_task
from django.utils import timezone
from inkmail.helpers import queue_transactional_message, queue_message
SEND_AFTER_PREVIOUS_DAY_HOURS = 22


@task
def send_purchase_email(purchase_pk):
    from products.models import ProductPurchase
    pp = ProductPurchase.objects.get(pk=purchase_pk)
    if not pp.purchase_email_sent:
        # Base on product name, context given by purchase
        om = queue_transactional_message(pp.product.purchase_message, pp.purchase.person, productpurchase=pp)
        pp.purchase_message = om
        pp.purchase_email_sent = True
        pp.save()


@periodic_task(run_every=datetime.timedelta(minutes=30), expires=600)
def send_pre_day_emails():
    from products.models import Journey, ProductDay
    now = timezone.now()
    for j in Journey.objects.filter(productpurchase__purchase__person__turned_off_product_emails=False).all():
        last_day = j.days.filter(completed=True).order_by("-day_number").first()
        if last_day:
            next_day = j.days.filter(completed=False, day_number__gt=last_day.day_number).order_by("day_number").first()

        if (
            last_day
            and next_day
            and not next_day.pre_day_email_sent
            and last_day.completed_at + datetime.timedelta(hours=SEND_AFTER_PREVIOUS_DAY_HOURS) <= now
        ):
            try:
                pd = ProductDay.objects.get(product=j.product, day_number=next_day.day_number)
                # Send email
                pp = j.productpurchase
                queue_transactional_message(pd.pre_day_message, pp.purchase.person, productpurchase=pp, journey_day=next_day)
                next_day.pre_day_email_sent = True
                next_day.save()
            except:
                print(last_day.hashid)
                print(next_day.hashid)
                print(j.hashid)
                import traceback
                traceback.print_exc()


@task
def notify_me(purchase_pk):
    from products.models import ProductPurchase
    pp = ProductPurchase.objects.get(pk=purchase_pk)
    if not pp.notification_email_sent:
        product_name = pp.product.name
        if pp.purchase.person.first_name:
            person_name = "%s (%s)" % (pp.purchase.person.first_name, pp.purchase.person.email)
        else:
            person_name = pp.purchase.person.email
        if pp.purchase.help_edition:
            product_name = "%s (Help Edition)" % product_name

        body = """
    Hey there,

    Great news!  %s just bought the %s!

    Woo! 🎉🎉🎉

    Have a great day,

    -The helpful inkshop robots :)

    """ % (person_name, product_name)
        django_send_mail(
            "💰 New Sale of %s!" % product_name, body, settings.INKSHOP_FROM_EMAIL,
            [settings.INKSHOP_ADMIN_EMAIL, ], fail_silently=False
        )
        pp.notification_email_sent = True
        pp.save()
