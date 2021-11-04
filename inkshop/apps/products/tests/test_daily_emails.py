from freezegun import freeze_time
import datetime
import logging
import json
import mock
import unittest

from utils.helpers import reverse
from django.core import mail
from django.conf import settings
from django.test.utils import override_settings
from django.utils import timezone

from people.models import Person
from products.models import Journey, JourneyDay, ProductDay
from products.tasks import send_pre_day_emails
from inkmail.models import Subscription, Message
from inkmail.tasks import process_outgoing_message_queue
from utils.factory import Factory
from utils.test_helpers import MailTestCase
from utils.encryption import normalize_lower_and_encrypt, normalize_and_encrypt, encrypt, decrypt


class TestDailyEmails(MailTestCase):

    def setUp(self, *args, **kwargs):
        self.person = Factory.person()
        self.product = Factory.product(has_epilogue=True)
        self.purchase = Factory.productpurchase(person=self.person, product=self.product)
        self.journey = Journey.objects.create(productpurchase=self.purchase, start_date=timezone.now())
        self.day1 = self.journey.days[0]
        # self.pw = Factory.rand_str(include_emoji=False)
        # self.person.set_password(self.pw)

        super(TestDailyEmails, self).setUp(*args, **kwargs)

    def test_day_two_email_sends(self):
        self.day1.completed = True
        self.day1.completed_at = timezone.now()
        self.day1.save()
        self.assertEquals(len(mail.outbox), 0)

        send_pre_day_emails()
        self.assertEquals(len(mail.outbox), 0)

        with freeze_time(self.now() + datetime.timedelta(hours=21)):
            send_pre_day_emails()
            self.assertEquals(len(mail.outbox), 0)

        with freeze_time(self.now() + datetime.timedelta(hours=23)):
            send_pre_day_emails()
            self.assertEquals(len(mail.outbox), 1)

    def test_email_content_is_right(self):
        m = self.product.productday_set.get(day_number=2).pre_day_message
        m.body_text_unrendered = """Hey {{ first_name | capfirst }},

Day 2 of your 7-Day Sprint is ready for you!

[Click here go to straight to it.](https://courses.inkandfeet.com{% url 'products:day' journey_day.hashid %}) :)

Enjoy!

-Steven
"""
        m.save()

        self.day1.completed = True
        self.day1.completed_at = timezone.now()
        self.day1.save()
        self.assertEquals(len(mail.outbox), 0)

        with freeze_time(self.now() + datetime.timedelta(hours=23)):
            send_pre_day_emails()
            self.assertEquals(len(mail.outbox), 1)
            self.assertIn("/courses/day/", mail.outbox[0].body)

    def test_all_emails_send_for_seven_day_sequence(self):
        self.seven_product = Factory.product(number_of_days=8, has_epilogue=True)
        self.purchase = Factory.productpurchase(person=self.person, product=self.seven_product)
        journey = Journey.objects.create(productpurchase=self.purchase, start_date=timezone.now())

        day = journey.days[0]
        day.completed = True
        day.completed_at = timezone.now()
        day.save()
        self.assertEquals(len(mail.outbox), 0)

        send_pre_day_emails()
        self.assertEquals(len(mail.outbox), 0)

        # Day 2
        with freeze_time(self.now() + datetime.timedelta(hours=23 + 0)):
            send_pre_day_emails()
            self.assertEquals(len(mail.outbox), 1)

            day = journey.days[1]
            day.completed = True
            day.completed_at = self.now()
            day.save()

            send_pre_day_emails()

        # Day 3
        with freeze_time(self.now() + datetime.timedelta(hours=23 + 24 * 1)):
            send_pre_day_emails()
            self.assertEquals(len(mail.outbox), 2)

            day = journey.days[2]
            day.completed = True
            day.completed_at = self.now()
            day.save()
            send_pre_day_emails()

        # Day 4
        with freeze_time(self.now() + datetime.timedelta(hours=23 + 24 * 2)):
            send_pre_day_emails()
            self.assertEquals(len(mail.outbox), 3)

            day = journey.days[3]
            day.completed = True
            day.completed_at = self.now()
            day.save()
            send_pre_day_emails()

        # Day 5
        with freeze_time(self.now() + datetime.timedelta(hours=23 + 24 * 3)):
            send_pre_day_emails()
            self.assertEquals(len(mail.outbox), 4)

            day = journey.days[4]
            day.completed = True
            day.completed_at = self.now()
            day.save()
            send_pre_day_emails()

        # Day 6
        with freeze_time(self.now() + datetime.timedelta(hours=23 + 24 * 4)):
            send_pre_day_emails()
            self.assertEquals(len(mail.outbox), 5)

            day = journey.days[5]
            day.completed = True
            day.completed_at = self.now()
            day.save()
            send_pre_day_emails()

        # Day 7
        with freeze_time(self.now() + datetime.timedelta(hours=23 + 24 * 5)):
            send_pre_day_emails()
            self.assertEquals(len(mail.outbox), 6)

            day = journey.days[6]
            day.completed = True
            day.completed_at = self.now()
            day.save()
            send_pre_day_emails()

        # Epilogue
        with freeze_time(self.now() + datetime.timedelta(hours=23 + 24 * 6)):
            send_pre_day_emails()
            self.assertEquals(len(mail.outbox), 7)

            day = journey.days[7]
            day.completed = True
            day.completed_at = self.now()
            day.save()
            send_pre_day_emails()

    def test_email_is_skipped_if_you_come_back_first(self):
        self.seven_product = Factory.product(number_of_days=8, has_epilogue=True)
        self.purchase = Factory.productpurchase(person=self.person, product=self.seven_product)
        journey = Journey.objects.create(productpurchase=self.purchase, start_date=timezone.now())

        day = journey.days[0]
        day.completed = True
        day.completed_at = timezone.now()
        day.save()
        self.assertEquals(len(mail.outbox), 0)

        send_pre_day_emails()
        self.assertEquals(len(mail.outbox), 0)

        # Day 2
        with freeze_time(self.now() + datetime.timedelta(hours=12 + 0)):
            send_pre_day_emails()
            # I came back early for day 2, no email sent.
            self.assertEquals(len(mail.outbox), 0)

            day = journey.days[1]
            day.completed = True
            day.completed_at = self.now()
            day.save()

            send_pre_day_emails()

        # Day 3
        with freeze_time(self.now() + datetime.timedelta(hours=23 + 24 * 1)):
            send_pre_day_emails()
            # I forgot day 3, email sent.
            self.assertEquals(len(mail.outbox), 1)

    def test_only_one_email_per_day(self):
        self.day1.completed = True
        self.day1.completed_at = timezone.now()
        self.day1.save()
        send_pre_day_emails()
        self.assertEquals(len(mail.outbox), 0)

        with freeze_time(self.now() + datetime.timedelta(hours=23)):
            send_pre_day_emails()
            send_pre_day_emails()
            send_pre_day_emails()
            send_pre_day_emails()
            self.assertEquals(len(mail.outbox), 1)

        with freeze_time(self.now() + datetime.timedelta(hours=96)):
            send_pre_day_emails()
            send_pre_day_emails()
            send_pre_day_emails()
            send_pre_day_emails()
            self.assertEquals(len(mail.outbox), 1)

    def test_no_email_until_day_two(self):
        send_pre_day_emails()
        self.assertEquals(len(mail.outbox), 0)

        with freeze_time(self.now() + datetime.timedelta(hours=23)):
            send_pre_day_emails()
            self.assertEquals(len(mail.outbox), 0)

        with freeze_time(self.now() + datetime.timedelta(hours=56)):
            send_pre_day_emails()
            self.assertEquals(len(mail.outbox), 0)

    def test_existing_users_mid_sequence_pre_email_handled(self):
        self.seven_product = Factory.product(number_of_days=8, has_epilogue=True)
        self.purchase = Factory.productpurchase(person=self.person, product=self.seven_product)
        journey = Journey.objects.create(productpurchase=self.purchase, start_date=timezone.now())

        day = journey.days[0]
        day.completed = True
        day.completed_at = timezone.now()
        day.save()

        self.assertEquals(len(mail.outbox), 0)

        # Day 2
        with freeze_time(self.now() + datetime.timedelta(hours=12 + 0)):
            day = journey.days[1]
            day.completed = True
            day.completed_at = self.now()
            day.save()

        # Day 3
        with freeze_time(self.now() + datetime.timedelta(hours=12 + 24)):
            day = journey.days[2]
            day.completed = True
            day.completed_at = self.now()
            day.save()

        # Day 4
        with freeze_time(self.now() + datetime.timedelta(hours=12 + 45)):
            day = journey.days[3]
            day.completed = True
            day.completed_at = self.now()
            day.save()

        # They stopped last week
        with freeze_time(self.now() + datetime.timedelta(hours=12 + 24 * 8)):
            send_pre_day_emails()
            self.assertEquals(len(mail.outbox), 1)
            self.assertIn(ProductDay.objects.get(
                day_number=5,
                product=self.seven_product
            ).pre_day_message.body_text_unrendered, mail.outbox[0].body)

    def test_existing_users_finished_sequence_emails_handled(self):
        self.seven_product = Factory.product(number_of_days=8, has_epilogue=True)
        self.purchase = Factory.productpurchase(person=self.person, product=self.seven_product)
        journey = Journey.objects.create(productpurchase=self.purchase, start_date=timezone.now())

        day = journey.days[0]
        day.completed = True
        day.completed_at = timezone.now()
        day.save()

        self.assertEquals(len(mail.outbox), 0)

        # Day 2
        with freeze_time(self.now() + datetime.timedelta(hours=12 + 0)):
            day = journey.days[1]
            day.completed = True
            day.completed_at = self.now()
            day.save()

        # Day 3
        with freeze_time(self.now() + datetime.timedelta(hours=12 + 24)):
            day = journey.days[2]
            day.completed = True
            day.completed_at = self.now()
            day.save()

        # Day 4
        with freeze_time(self.now() + datetime.timedelta(hours=12 + 45)):
            day = journey.days[3]
            day.completed = True
            day.completed_at = self.now()
            day.save()

        with freeze_time(self.now() + datetime.timedelta(hours=12 + 24 * 3)):
            day = journey.days[4]
            day.completed = True
            day.completed_at = self.now()
            day.save()

        with freeze_time(self.now() + datetime.timedelta(hours=12 + 24 * 4)):
            day = journey.days[5]
            day.completed = True
            day.completed_at = self.now()
            day.save()

        with freeze_time(self.now() + datetime.timedelta(hours=12 + 24 * 5)):
            day = journey.days[6]
            day.completed = True
            day.completed_at = self.now()
            day.save()

        with freeze_time(self.now() + datetime.timedelta(hours=12 + 24 * 6)):
            day = journey.days[7]
            day.completed = True
            day.completed_at = self.now()
            day.save()

        # They finished last week
        with freeze_time(self.now() + datetime.timedelta(hours=12 + 24 * 8)):
            send_pre_day_emails()
            send_pre_day_emails()
            self.assertEquals(len(mail.outbox), 0)

    def test_existing_users_crazy_missing_days_handled(self):
        self.seven_product = Factory.product(number_of_days=8, has_epilogue=True)
        self.purchase = Factory.productpurchase(person=self.person, product=self.seven_product)
        journey = Journey.objects.create(productpurchase=self.purchase, start_date=timezone.now())

        day = journey.days[0]
        day.completed = True
        day.completed_at = timezone.now()
        day.save()
        self.assertEquals(len(mail.outbox), 0)

        # Day 2
        with freeze_time(self.now() + datetime.timedelta(hours=12 + 0)):
            day = journey.days[1]
            day.completed = True
            day.completed_at = self.now()
            day.save()

        # Day 3
        with freeze_time(self.now() + datetime.timedelta(hours=12 + 24)):
            day = journey.days[2]
            day.completed = True
            day.completed_at = self.now()
            day.save()

        # Day 4
        with freeze_time(self.now() + datetime.timedelta(hours=12 + 45)):
            day = journey.days[3]
            day.completed = True
            day.completed_at = self.now()
            day.save()

        # Somehow skip completing day 5, do day 6 though.
        with freeze_time(self.now() + datetime.timedelta(hours=12 + 24 * 3)):
            day = journey.days[5]
            day.completed = True
            day.completed_at = self.now()
            day.save()

        # Then, they stopped last week.
        # Should be for day 7, I guess.
        with freeze_time(self.now() + datetime.timedelta(hours=12 + 24 * 12)):
            send_pre_day_emails()
            self.assertEquals(len(mail.outbox), 1)
            self.assertIn(ProductDay.objects.get(
                day_number=7,
                product=self.seven_product
            ).pre_day_message.body_text_unrendered, mail.outbox[0].body)

    def test_emails_turned_off_doesnt_send(self):
        self.person.turned_off_product_emails = True
        self.person.save()
        self.day1.completed = True
        self.day1.completed_at = timezone.now()
        self.day1.save()
        self.assertEquals(len(mail.outbox), 0)

        send_pre_day_emails()
        self.assertEquals(len(mail.outbox), 0)

        with freeze_time(self.now() + datetime.timedelta(hours=21)):
            send_pre_day_emails()
            self.assertEquals(len(mail.outbox), 0)

        with freeze_time(self.now() + datetime.timedelta(hours=23)):
            send_pre_day_emails()
            self.assertEquals(len(mail.outbox), 0)

        with freeze_time(self.now() + datetime.timedelta(hours=48)):
            send_pre_day_emails()
            self.assertEquals(len(mail.outbox), 0)
