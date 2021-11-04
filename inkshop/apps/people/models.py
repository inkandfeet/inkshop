import datetime
import hashlib
import logging
import json
import jwt
import random
import time
import uuid
from base64 import b64encode
from io import BytesIO
from PIL import Image, ImageOps
from tempfile import NamedTemporaryFile
from urllib.parse import urlencode, quote_plus

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.contrib.auth.signals import user_logged_in
from utils.helpers import reverse
from django.utils.functional import cached_property
from django.utils import timezone

from clubhouse.models import UserManager
from utils.models import HashidBaseModel, HasJWTBaseModel
from utils.encryption import encrypt, decrypt, lookup_hash


class Person(AbstractBaseUser, HasJWTBaseModel, HashidBaseModel):
    USERNAME_FIELD = 'hashed_email'
    encrypted_first_name = models.CharField(max_length=4096, blank=True, null=True)
    encrypted_last_name = models.CharField(max_length=4096, blank=True, null=True)
    encrypted_email = models.CharField(unique=True, max_length=4096, blank=True, null=True,)
    hashed_first_name = models.CharField(max_length=4096, blank=True, null=True)
    hashed_last_name = models.CharField(max_length=4096, blank=True, null=True)
    hashed_email = models.CharField(unique=True, max_length=4096, blank=True, null=True, verbose_name="Email")
    email_verified = models.BooleanField(default=False)
    time_zone = models.CharField(max_length=254, blank=True, null=True,)

    was_imported = models.BooleanField(default=False)
    was_imported_at = models.DateTimeField(blank=True, null=True)
    import_source = models.CharField(max_length=254, blank=True, null=True)
    patron = models.BooleanField(default=False)

    marked_troll = models.BooleanField(default=False)
    marked_troll_at = models.DateTimeField(blank=True, null=True)
    banned = models.BooleanField(default=False)
    banned_at = models.DateTimeField(blank=True, null=True)
    hard_bounced = models.BooleanField(default=False)
    hard_bounced_at = models.DateTimeField(blank=True, null=True)
    hard_bounced_reason = models.TextField(blank=True, null=True)
    hard_bounced_message = models.ForeignKey('inkmail.Message', blank=True, null=True, on_delete=models.SET_NULL)

    never_contact_set = models.BooleanField(default=False)
    never_contact_set_at = models.DateTimeField(blank=True, null=True)

    personal_contact = models.BooleanField(default=False)

    encrypted_data = models.TextField(blank=True, null=True,)
    is_staff = models.BooleanField(default=False)

    turned_off_product_emails = models.BooleanField(default=False)
    # hashed_data = models.CharField(unique=True, max_length=4096, blank=True, null=True, verbose_name="Email")

    objects = UserManager()

    def __str__(self):
        return self.hashid

    @classmethod
    def get_by_email(cls, email):
        if cls.objects.filter(hashed_email=lookup_hash(email)).count() > 0:
            return cls.objects.get(hashed_email=lookup_hash(email))
        return None

    @property
    def email(self):
        if not hasattr(self, "_decrypted_email"):
            self._decrypted_email = decrypt(self.encrypted_email)
        return self._decrypted_email

    @email.setter
    def email(self, value):
        self.encrypted_email = encrypt(value)
        self.hashed_email = lookup_hash(value)

    @property
    def first_name(self):
        if not hasattr(self, "_decrypted_first_name"):
            self._decrypted_first_name = decrypt(self.encrypted_first_name)
        return self._decrypted_first_name

    @first_name.setter
    def first_name(self, value):
        self.encrypted_first_name = encrypt(value)
        self.hashed_first_name = lookup_hash(value)

    @property
    def last_name(self):
        if not hasattr(self, "_decrypted_last_name"):
            self._decrypted_last_name = decrypt(self.encrypted_last_name)
        return self._decrypted_last_name

    @property
    def full_name(self):
        return "%s %s" % (self.first_name, self.last_name, )

    @last_name.setter
    def last_name(self, value):
        self.encrypted_last_name = encrypt(value)
        self.hashed_last_name = lookup_hash(value)

    def ban(self):
        from archives.models import HistoricalEvent
        if not self.banned:
            self.banned = True
            self.banned_at = timezone.now()
            self.save()
            HistoricalEvent.log(person=self, event_type="ban")

    def mark_troll(self):
        from archives.models import HistoricalEvent
        if not self.marked_troll:
            self.marked_troll = True
            self.marked_troll_at = timezone.now()
            self.save()
            HistoricalEvent.log(person=self, event_type="mark_troll")

    def hard_bounce(self, reason=None, bouncing_message=None, raw_mailgun_data={}):
        from archives.models import HistoricalEvent
        if not self.hard_bounced:
            self.hard_bounced = True
            self.hard_bounced_at = timezone.now()
            self.hard_bounced_reason = reason
            self.hard_bounced_message = bouncing_message
            self.save()
            HistoricalEvent.log(
                person=self,
                event_type="mark_hard_bounce",
                reason=reason,
                message=bouncing_message,
                raw_mailgun_data=raw_mailgun_data,
            )

    @property
    def data(self):
        if not hasattr(self, "_decrypted_data"):
            self._decrypted_data = decrypt(self.encrypted_data)
        return self._decrypted_data

    @data.setter
    def data(self, value):
        self.encrypted_data = encrypt(value)
        # self.hashed_email = lookup_hash(value)

    @cached_property
    def python_data(self):
        if self.data:
            return json.loads(self.data)
        return {}

    @cached_property
    def gdpr_dump(self):
        data = {
            "person": {
                'first_name': self.first_name,
                'last_name': self.last_name,
                'email': self.email,
                'time_zone': self.time_zone,
                'patron': self.patron,
                'never_contact_set': self.never_contact_set,
                'never_contact_set_at': self.never_contact_set_at,
                'marked_troll': self.marked_troll,
                'marked_troll_at': self.marked_troll_at,
                'banned': self.banned,
                'banned_at': self.banned_at,
                'hard_bounced': self.hard_bounced,
                'hard_bounced_at': self.hard_bounced_at,
                'hard_bounced_reason': self.hard_bounced_reason,
                'hard_bounced_message': self.hard_bounced_message,
                'data': self.python_data,
            },
            "products": {},
            "purchases": {},
            "subscriptions": {},
            "emails_sent": [],
        }
        for p in self.products:
            data['products'][p.product.slug] = {

            }
            for j in p.journeys:
                data['products'][p.product.slug]['journey-%s' % j.start_date.strftime('%Y-%m-%d')] = {
                    'data': j.python_data,
                }

                for d in j.days:
                    data['products'][p.product.slug][
                        'journey-%s' % j.start_date.strftime('%Y-%m-%d')
                    ]['day-%s' % d.day_number] = {
                        'data': d.python_data,
                        'day_number': d.day_number,
                        'start_date': d.start_date,
                        'first_user_action': d.first_user_action,
                        'last_user_action': d.last_user_action,
                        'completed': d.completed,
                        'completed_at': d.completed_at,
                    }

        for pp in self.purchases:
            p = pp.purchase
            data['purchases'][p.hashid] = {
                "total": p.total,
                "discount_code": p.discount_code,
                "discount_amount": p.discount_amount,
                "stripe_payment_confirmed_at": p.stripe_payment_confirmed_at,
                "refunded": p.refunded,
                "refunded_at": p.refunded_at,
                "refund_feedback": p.refund_feedback,
            }

        for s in self.subscriptions:
            if s.newsletter:
                data['subscriptions'][s.newsletter.internal_name] = {
                    "subscribed_at": s.subscribed_at,
                    "subscription_url": s.subscription_url,
                    "subscribed_from_ip": s.subscribed_from_ip,
                    "was_imported": s.was_imported,
                    "was_imported_at": s.was_imported_at,
                    "import_source": s.import_source,
                    "double_opted_in": s.double_opted_in,
                    "double_opted_in_at": s.double_opted_in_at,
                    "has_set_never_unsubscribe": s.has_set_never_unsubscribe,
                    "unsubscribed": s.unsubscribed,
                    "unsubscribed_at": s.unsubscribed_at,
                    "last_action": s.last_action,
                }

        for e in self.emails:
            subscription = None
            if e.subscription and e.subscription.newsletter:
                subscription = e.subscription.newsletter.internal_name

            data['emails_sent'].append({
                "message": e.message.subject,
                "subscription": subscription,
                "send_at": e.send_at,
                "loved": e.loved,
                "loved_at": e.loved_at,
                "attempt_started": e.attempt_started,
                "attempt_complete": e.attempt_complete,
                "attempt_completed_at": e.attempt_completed_at,
                "attempt_skipped": e.attempt_skipped,
                "attempt_count": e.attempt_count,
                "valid_message": e.valid_message,
                "send_success": e.send_success,
                "hard_bounced": e.hard_bounced,
                "hard_bounced_at": e.hard_bounced_at,
                "hard_bounce_reason": e.hard_bounce_reason,
            })
        return data

    def messages_sent(self):
        return self.outgoingmessage_set.order_by("created_at").all()

    @cached_property
    def products(self):
        from products.models import ProductPurchase
        return ProductPurchase.objects.filter(purchase__person=self, purchase__refunded=False).all()

    @cached_property
    def purchases(self):
        from products.models import ProductPurchase
        return ProductPurchase.objects.filter(purchase__person=self).all()

    @cached_property
    def subscriptions(self):
        from inkmail.models import Subscription
        return Subscription.objects.filter(person=self)

    @cached_property
    def emails(self):
        from inkmail.models import OutgoingMessage
        return OutgoingMessage.objects.filter(person=self)

    @cached_property
    def has_course(self):
        return self.products.filter(product__is_course=True).count() > 0

    @cached_property
    def has_download(self):
        return self.products.filter(product__is_downloadable=True).count() > 0

    def one_click_sign_in_link(self, url):
        from utils.factory import Factory
        return quote_plus(encrypt("%s|%s|%s" % (Factory.rand_str(include_emoji=False, length=5), self.hashid, url)))
