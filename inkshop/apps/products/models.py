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

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.contrib.auth.signals import user_logged_in
from utils.helpers import reverse
from django.utils.functional import cached_property
from django.utils.text import slugify
from django.utils import timezone
import stripe

from products.tasks import send_purchase_email, notify_me
from utils.models import HashidBaseModel, HasJWTBaseModel
from utils.encryption import encrypt, decrypt, lookup_hash

stripe.api_key = settings.STRIPE_SECRET_KEY


class Product(HashidBaseModel):
    name = models.CharField(max_length=512)
    slug = models.CharField(max_length=254, blank=True, null=True)
    number_of_days = models.IntegerField(blank=True, null=True,)
    has_epilogue = models.BooleanField(default=False)
    stripe_product_id = models.CharField(max_length=512, blank=True, null=True)
    stripe_price_id = models.CharField(max_length=512, blank=True, null=True)
    stripe_beta_price_id = models.CharField(max_length=512, blank=True, null=True)
    purchase_message = models.ForeignKey('inkmail.Message', blank=True, null=True, on_delete=models.SET_NULL)
    journey_singular_name = models.CharField(max_length=512, blank=True, null=True)
    journey_plural_name = models.CharField(max_length=512, blank=True, null=True)
    is_course = models.BooleanField(default=False)
    is_downloadable = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.name and not self.slug:
            self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    @cached_property
    def share_link(self):
        return "https://share.inkandfeet.com/"

    @property
    def feedback(self):
        return self.productfeedback_set.all()

    @classmethod
    def get_from_slug(cls, slug):
        if hasattr(cls, "_product_%s" % slug):
            return getattr(cls, "_product_%s" % slug)
        p = cache.get("inkshop.Product.%s" % slug)
        if p:
            return p
        else:
            setattr(cls, "_product_%s" % slug, cls.objects.get(slug=slug))
            cache.set("inkshop.Product.%s" % slug, getattr(cls, "_product_%s" % slug))
            return getattr(cls, "_product_%s" % slug)


class ProductFeedback(HashidBaseModel):
    # name = models.CharField(max_length=512)
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    person = models.ForeignKey('people.Person', on_delete=models.SET_NULL, blank=True, null=True)
    raw_data = models.TextField(blank=True, null=True,)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    # hashed_data = models.CharField(unique=True, max_length=4096, blank=True, null=True, verbose_name="Email")

    @property
    def data(self):
        return json.loads(self.raw_data)


class ProductDay(HashidBaseModel):
    # name = models.CharField(max_length=512)
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    day_number = models.IntegerField(blank=True, null=True,)
    pre_day_message = models.ForeignKey(
        'inkmail.Message',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="daily_pre_message"
    )

    def __str__(self):
        return "%s - Day %s" % (self.product, self.day_number)


class Purchase(HashidBaseModel):
    person = models.ForeignKey('people.Person', on_delete=models.CASCADE, blank=True, null=True)
    total = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    discount_code = models.CharField(max_length=254, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    help_edition = models.BooleanField(default=False)
    stripe_session_id = models.CharField(max_length=512, blank=True, null=True)
    stripe_payment_intent_id = models.CharField(max_length=512, blank=True, null=True)
    stripe_payment_confirmed = models.BooleanField(default=False)
    stripe_payment_confirmed_at = models.DateTimeField(blank=True, null=True)
    refunded = models.BooleanField(default=False)
    refunded_at = models.DateTimeField(blank=True, null=True)
    refund_feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        try:
            return "%sPurchase by %s on %s" % (self.refunded_string, self.person, self.created_at)
        except:
            return "%sPurchase by unknown on %s" % (self.refunded_string, self.created_at, )

    @cached_property
    def refunded_string(self):
        if self.refunded:
            return "REFUNDED "
        return ""

    def refund(self, feedback=None):
        if not self.help_edition:
            stripe.Refund.create(payment_intent=self.stripe_payment_intent_id, reason="requested_by_customer")
        self.refunded = True
        self.refunded_at = timezone.now()
        self.refund_feedback = feedback
        self.save()


class ProductPurchase(HashidBaseModel):
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    purchase = models.ForeignKey(Purchase, null=True, on_delete=models.CASCADE)
    purchase_email_sent = models.BooleanField(default=False)
    notification_email_sent = models.BooleanField(default=False)
    purchase_message = models.ForeignKey(
        'inkmail.OutgoingMessage',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="purchase_reciept_message"
    )

    def __str__(self):
        try:
            return "Purchase of %s by %s on %s" % (self.product, self.purchase.person, self.created_at)
        except:
            return "Purchase of unknown by unknown on %s" % (self.created_at, )

    @property
    def journeys(self):
        return Journey.objects.filter(productpurchase=self).all().order_by("-created_at")

    @property
    def access_url(self):
        if self.product.is_course:
            return "https://%s/%s/" % (
                settings.PRODUCTS_DOMAIN,
                self.product.slug,
                # reverse('products:course_purchase', args=(self.product.slug, ))
            )
        else:
            return "https://%s/%s/" % (
                settings.SHOP_DOMAIN,
                self.product.slug,
                # reverse('products:course_purchase', args=(self.product.slug, ))
            )

    def send_purchase_email(self):
        send_purchase_email.delay(self.pk)
        notify_me.delay(self.pk)

    def one_click_sign_in_url(self):
        return self.purchase.person.one_click_sign_in_link(self.access_url)


class Journey(HashidBaseModel):
    productpurchase = models.ForeignKey(ProductPurchase, null=True, on_delete=models.CASCADE, blank=True)
    start_date = models.DateField(blank=True, default=timezone.now, null=True)

    def __str__(self):
        return "%s - %s @ %s" % (self.product, self.productpurchase, self.start_date)

    @cached_property
    def data(self):
        try:
            return json.loads(
                self.productpurchase.purchase.person.data
            )["products"][self.productpurchase.product.slug][self.hashid]
        except:
            return None

    @cached_property
    def json_data(self):
        # I know. This is ridiculous
        return json.dumps(self.data)

    @cached_property
    def python_data(self):
        if self.data:
            return self.data
        return {}

    @cached_property
    def product(self):
        if self.productpurchase:
            return self.productpurchase.product
        return None

    @property
    def days(self):
        return JourneyDay.objects.filter(journey=self).all().order_by("day_number")

    @cached_property
    def journey_num(self):
        index = 0
        for j in self.productpurchase.journey_set.all().order_by("start_date"):
            index += 1
            if j.pk == self.pk:
                return index
        return index

    @property
    def journey_singular_name(self):
        return self.productpurchase.product.journey_singular_name

    @property
    def journey_plural_name(self):
        return self.productpurchase.product.journey_plural_name

    @cached_property
    def discount_code(self):
        return "FINISHER25"

    @cached_property
    def discount_code_amount(self):
        return 25


class JourneyDay(HashidBaseModel):
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE)
    day_number = models.IntegerField()
    start_date = models.DateTimeField(blank=True, null=True, default=timezone.now)
    first_user_action = models.DateTimeField(blank=True, null=True)
    last_user_action = models.DateTimeField(blank=True, null=True)
    encrypted_data = models.TextField(blank=True, null=True,)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    pre_day_email_sent = models.BooleanField(default=False)
    # hashed_data = models.CharField(unique=True, max_length=4096, blank=True, null=True, verbose_name="Email")

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
    def productday(self):
        return self.journey.product.productday_set.all().filter(day_number=self.day_number)[0]

    @cached_property
    def visible(self):
        if not self.journey.product.has_epilogue or self.day_number < self.journey.days.count():
            return True
        if self.journey.days.get(day_number=self.day_number - 1).last_user_action:
            return True

        return False

    @cached_property
    def most_recent_day_first_action(self):
        try:
            return self.journey.days.get(day_number=self.day_number - 1).first_user_action
        except:
            return None

    @cached_property
    def hypothetical_start_date(self):
        completed_days = self.journey.days.filter(completed=True).order_by("-day_number")
        if completed_days.count() > 0:
            last_day_completed_day = completed_days[0]
            return last_day_completed_day.completed_at + datetime.timedelta(
                days=self.day_number - last_day_completed_day.day_number
            )
        else:
            first_days = self.journey.days.filter(first_user_action__isnull=False).order_by("day_number")
            if first_days.count() > 0:
                first_day = first_days[0]
                return first_day.first_user_action + datetime.timedelta(
                    days=self.day_number - first_day.day_number
                )
        return None

    @cached_property
    def available(self):
        # TODO decide on this: for now recommend_available
        # self.most_recent_day_first_action > timezone.now() + datetime.timedelta(hours=6)
        if self.day_number == 1 or self.most_recent_day_first_action:
            return True

        return False

    @cached_property
    def recommend_available(self):
        if (
            self.day_number == 1
            or (
                self.most_recent_day_first_action
                and timezone.now() > self.most_recent_day_first_action + datetime.timedelta(hours=6)
            )
        ):
            return True

        return False

    @cached_property
    def is_current(self):
        completed_days = self.journey.days.filter(completed=True).order_by("-day_number")
        if completed_days.count() > 0:
            last_day_completed_day = completed_days[0]
            if self.day_number == last_day_completed_day.day_number + 1 and not self.completed:
                return True
        else:
            if self.day_number == 1 and not self.completed:
                return True
        return False

    @cached_property
    def is_epilogue(self):
        if not self.journey.product.has_epilogue or self.day_number < self.journey.days.count():
            return False
        return True


@receiver(post_save, sender=Journey)
def create_journey_days(sender, instance, created, **kwargs):
    """Create matching JourneyDays whenever a Journey object is created."""
    if created:
        for i in range(0, instance.product.number_of_days):
            JourneyDay.objects.create(
                day_number=i + 1,
                journey=instance,
            )


class BestimatorExperiment(HashidBaseModel):
    name = models.CharField(max_length=512)
    slug = models.CharField(max_length=254, blank=True, null=True)

    def __str__(self):
        if self.name:
            return "%s" % (self.name, )
        return ""

    def choices(self):
        return self.bestimatorexperimentchoice_set.all()


class BestimatorExperimentChoice(HashidBaseModel):
    name = models.CharField(max_length=512)
    experiment = models.ForeignKey(BestimatorExperiment, blank=True, null=True, on_delete=models.CASCADE)
    slug = models.CharField(max_length=254, blank=True, null=True)
    url = models.CharField(max_length=512, blank=True, null=True)
    pattern = models.CharField(max_length=512, blank=True, null=True)
    template_name = models.CharField(max_length=512, blank=True, null=True)

    def __str__(self):
        if self.name and self.experiment:
            return "%s: %s" % (self.experiment, self.name,)
        if self.name:
            return "%s" % (self.name, )
        return ""

    @cached_property
    def num_answers(self):
        return self.bestimatoranswer_set.all().count()

    @cached_property
    def num_feels_grin(self):
        return self.bestimatoranswer_set.all().filter(feels_grin=True).count()

    @cached_property
    def percent_feels_grin(self):
        return 100.0 * self.num_feels_grin / self.num_answers

    @cached_property
    def num_feels_laugh_cry(self):
        return self.bestimatoranswer_set.all().filter(feels_laugh_cry=True).count()

    @cached_property
    def percent_feels_laugh_cry(self):
        return 100.0 * self.num_feels_laugh_cry / self.num_answers

    @cached_property
    def num_feels_love(self):
        return self.bestimatoranswer_set.all().filter(feels_love=True).count()

    @cached_property
    def percent_feels_love(self):
        return 100.0 * self.num_feels_love / self.num_answers

    @cached_property
    def num_feels_hmm(self):
        return self.bestimatoranswer_set.all().filter(feels_hmm=True).count()

    @cached_property
    def percent_feels_hmm(self):
        return 100.0 * self.num_feels_hmm / self.num_answers

    @cached_property
    def num_feels_embarrased(self):
        return self.bestimatoranswer_set.all().filter(feels_embarrased=True).count()

    @cached_property
    def percent_feels_embarrased(self):
        return 100.0 * self.num_feels_embarrased / self.num_answers

    @cached_property
    def num_feels_shocked(self):
        return self.bestimatoranswer_set.all().filter(feels_shocked=True).count()

    @cached_property
    def percent_feels_shocked(self):
        return 100.0 * self.num_feels_shocked / self.num_answers

    @cached_property
    def num_feels_sick(self):
        return self.bestimatoranswer_set.all().filter(feels_sick=True).count()

    @cached_property
    def percent_feels_sick(self):
        return 100.0 * self.num_feels_sick / self.num_answers

    @cached_property
    def num_feels_angry(self):
        return self.bestimatoranswer_set.all().filter(feels_angry=True).count()

    @cached_property
    def percent_feels_angry(self):
        return 100.0 * self.num_feels_angry / self.num_answers

    @cached_property
    def num_buy_clicked(self):
        return self.bestimatoranswer_set.all().filter(buy_clicked=True).count()

    @cached_property
    def percent_buy_clicked(self):
        return 100.0 * self.num_buy_clicked / self.num_answers

    @cached_property
    def num_authentic_yes(self):
        return self.bestimatoranswer_set.all().filter(authentic=True).count()

    @cached_property
    def num_authentic_no(self):
        return self.bestimatoranswer_set.all().filter(authentic=False).count()

    @cached_property
    def num_good_value_yes(self):
        return self.bestimatoranswer_set.all().filter(good_value=True).count()

    @cached_property
    def num_good_value_no(self):
        return self.bestimatoranswer_set.all().filter(good_value=False).count()

    @cached_property
    def num_want_to_buy_yes(self):
        return self.bestimatoranswer_set.all().filter(want_to_buy=True).count()

    @cached_property
    def num_want_to_buy_no(self):
        return self.bestimatoranswer_set.all().filter(want_to_buy=False).count()

    @cached_property
    def percent_want_to_buy(self):
        return 100.0 * (self.num_want_to_buy_yes / (self.num_want_to_buy_no + self.num_want_to_buy_yes))

    @cached_property
    def answers_with_comments(self):
        return self.bestimatoranswer_set.all().exclude(other_comments=None).exclude(other_comments="")


class BestimatorAnswer(HashidBaseModel):
    session_hash = models.CharField(max_length=512)
    experiment_choice = models.ForeignKey(BestimatorExperimentChoice, blank=True, null=True, on_delete=models.CASCADE)

    feels_grin = models.BooleanField(blank=True, null=True)
    feels_laugh_cry = models.BooleanField(blank=True, null=True)
    feels_love = models.BooleanField(blank=True, null=True)
    feels_hmm = models.BooleanField(blank=True, null=True)
    feels_embarrased = models.BooleanField(blank=True, null=True)
    feels_shocked = models.BooleanField(blank=True, null=True)
    feels_sick = models.BooleanField(blank=True, null=True)
    feels_angry = models.BooleanField(blank=True, null=True)

    # feel authentic and honest?
    authentic = models.BooleanField(blank=True, null=True)

    # feel like good value?
    good_value = models.BooleanField(blank=True, null=True)

    # does it make you interested in buying?
    buy_clicked = models.BooleanField(blank=True, null=True)
    want_to_buy = models.BooleanField(blank=True, null=True)
    other_comments = models.TextField(blank=True, null=True)

    @cached_property
    def json_data(self):
        return json.dumps(self.data)

    @cached_property
    def data(self):
        return {
            "feels_grin": self.feels_grin,
            "feels_laugh_cry": self.feels_laugh_cry,
            "feels_love": self.feels_love,
            "feels_hmm": self.feels_hmm,
            "feels_embarrased": self.feels_embarrased,
            "feels_shocked": self.feels_shocked,
            "feels_sick": self.feels_sick,
            "feels_angry": self.feels_angry,
            "authentic": self.authentic,
            "good_value": self.good_value,
            "buy_clicked": self.buy_clicked,
            "want_to_buy": self.want_to_buy,
            "other_comments": self.other_comments,
        }
