# -*- coding: utf-8 -*-
import bleach
import datetime
import hashlib
import mistune
import logging
import random
import time
import uuid
from base64 import b64encode
from io import BytesIO
from PIL import Image, ImageOps
from tempfile import NamedTemporaryFile

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.files.base import ContentFile
from django.core.mail import send_mail as django_send_mail
from django.contrib.auth.signals import user_logged_in
from django.template.defaultfilters import linebreaks
from django.template.loader import render_to_string
from django.template import Template, Context
from utils.helpers import reverse
from django.utils.functional import cached_property
from django.utils import timezone

from people.models import Person
from utils.models import HashidBaseModel, BaseModel
from utils.encryption import lookup_hash, encrypt, decrypt, create_unique_hashid

markdown = mistune.Markdown()
OPT_IN_LINK_EXPIRE_TIME = datetime.timedelta(days=7)
RETRY_IN_TIME = datetime.timedelta(minutes=2)
ORG_SINGLETON_KEY = "KLJF83jlaesfkj"


class Organization(BaseModel):
    singleton_key = models.CharField(max_length=254, unique=True)
    name = models.CharField(max_length=254, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    transactional_footer = models.TextField(blank=True, null=True)
    favicon = models.ForeignKey('website.Resource', blank=True, null=True, on_delete=models.SET_NULL)

    @classmethod
    def get(cls):
        if not hasattr(cls, "_singleton"):
            cls._singleton, _ = cls.objects.get_or_create(singleton_key=ORG_SINGLETON_KEY)
        return cls._singleton

    def __str__(self):
        return "%s" % (self.name,)


class Message(HashidBaseModel):
    name = models.CharField(max_length=254, blank=True, null=True)
    subject = models.CharField(max_length=254, blank=True, null=True)
    body_text_unrendered = models.TextField(blank=True, null=True)
    body_html_unrendered = models.TextField(blank=True, null=True)
    reward_image = models.ImageField(
        verbose_name="Reward Image",
        upload_to='awesome',
        blank=True,
        null=True,
    )
    transactional = models.BooleanField(default=False)
    transactional_send_reason = models.CharField(max_length=254, blank=True, null=True)
    transactional_no_unsubscribe_reason = models.CharField(max_length=254, blank=True, null=True)

    def __str__(self):
        return "%s: %s" % (self.name, self.subject)


class Newsletter(HashidBaseModel):
    name = models.CharField(max_length=254, blank=True, null=True)
    internal_name = models.CharField(unique=True, max_length=254, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    from_email = models.TextField(max_length=254)
    from_name = models.TextField(max_length=254)
    unsubscribe_footer = models.TextField()

    confirm_message = models.ForeignKey(
        Message,
        on_delete=models.SET_NULL, blank=True, null=True, related_name="list_for_confirm"
    )
    welcome_message = models.ForeignKey(
        Message,
        on_delete=models.SET_NULL, blank=True, null=True, related_name="list_for_welcome"
    )

    unsubscribe_if_no_hearts_after_days = models.BooleanField(default=False)
    unsubscribe_if_no_hearts_after_days_num = models.IntegerField(blank=True, null=True, default=184)
    unsubscribe_if_no_hearts_after_messages = models.BooleanField(default=True)
    unsubscribe_if_no_hearts_after_messages_num = models.IntegerField(blank=True, null=True, default=26)

    def __str__(self):
        if self.name:
            return "%s" % (self.name, )
        return "%s" % self.internal_name

    @property
    def full_from_email(self):
        return '%s <%s>' % (self.from_name, self.from_email)

    @property
    def transfer_subscription_url(self):
        try:
            return "%s%s" % (
                settings.MAIL_BASE_URL,
                reverse("inkmail:transfer_subscription", args=(self.hashid, ), host='mail'),
            )
        except:
            return "%s%s" % (
                settings.MAIL_BASE_URL,
                "/mail/transfer-subscription/%s/" % self.hashid,
            )

    @classmethod
    def import_subscriber(
        cls,
        import_source,
        email,
        subscribed_at,
        subscription_url,
        double_opted_in,
        double_opted_in_at=None,
        hard_bounced=False,
        hard_bounced_at=None,
        hard_bounced_reason=None,
        first_name=None,
        last_name=None,
        subscription_ip=None,
        time_zone=None,
        newsletter_name=None,
        overwrite=False,
    ):
        newsletter = False
        if newsletter_name:
            newsletter = Newsletter.objects.get(internal_name=newsletter_name)

        hashed_email = lookup_hash(email)
        person_exists = False
        if Person.objects.filter(hashed_email=hashed_email).count() > 0:
            person_exists = True
            p = Person.objects.get(hashed_email=hashed_email)
            if p.banned:
                return
        else:
            p = Person.objects.create(
                hashed_email=hashed_email
            )

        if overwrite or not person_exists:
            p.first_name = first_name
            p.last_name = last_name
            p.email = email
            assert p.hashed_email == hashed_email
            p.email_verified = double_opted_in
            p.time_zone = time_zone
            p.was_imported = True
            p.was_imported_at = datetime.datetime.now(timezone.utc)
            p.hard_bounced = hard_bounced
            p.hard_bounced_at = hard_bounced_at
            p.hard_bounced_reason = hard_bounced_reason
            p.import_source = import_source
            p.save()

        if newsletter:
            if Subscription.objects.filter(person=p, newsletter=newsletter).count() > 0:
                if not overwrite:
                    return
                s = Subscription.objects.get(person=p, newsletter=newsletter)
            else:
                s = Subscription.objects.create(
                    person=p,
                    newsletter=newsletter
                )

            s.subscribed_at = p.was_imported_at
            s.subscription_url = subscription_url
            s.subscribed_from_ip = subscription_ip
            s.was_imported = True
            s.was_imported_at = p.was_imported_at
            s.import_source = import_source
            s.double_opted_in = double_opted_in
            s.double_opted_in_at = double_opted_in_at
            s.save()

    @property
    def subscriptions(self):
        return self.subscription_set.filter(unsubscribed=False, person__hard_bounced=False).select_related('person').all()


class Subscription(HashidBaseModel):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE)
    subscribed_at = models.DateTimeField(blank=True, null=True, default=timezone.now)
    subscription_url = models.TextField(blank=True, null=True)
    subscribed_from_ip = models.CharField(max_length=254, blank=True, null=True)
    was_imported = models.BooleanField(default=False)
    was_imported_at = models.DateTimeField(blank=True, null=True)
    import_source = models.CharField(max_length=254, blank=True, null=True)
    double_opted_in = models.BooleanField(default=False)
    double_opted_in_at = models.DateTimeField(blank=True, null=True)
    has_set_never_unsubscribe = models.BooleanField(default=False)
    unsubscribed = models.BooleanField(default=False)
    unsubscribed_at = models.DateTimeField(blank=True, null=True)

    opt_in_key = models.CharField(max_length=254, blank=True, null=True, db_index=True)
    opt_in_key_created_at = models.DateTimeField(blank=True, null=True)

    last_action = models.DateTimeField(blank=True, null=True, default=timezone.now)

    def unsubscribe(self):
        if not self.unsubscribed:
            self.unsubscribed = True
            self.unsubscribed_at = timezone.now()
            self.double_opted_in = False
            self.double_opted_in_at = None
            self.save()

    def double_opt_in(self):
        if not self.double_opted_in:
            self.double_opted_in = True
            self.double_opted_in_at = timezone.now()
            self.save()

    def generate_opt_in_link(self):
        self.opt_in_key = create_unique_hashid(self.pk, Subscription, "opt_in_key")
        self.opt_in_key_created_at = timezone.now()
        self.save()

    @property
    def opt_in_link(self):
        if not self.opt_in_key or self.opt_in_key_created_at < timezone.now() - OPT_IN_LINK_EXPIRE_TIME:
            self.generate_opt_in_link()

        return "%s%s" % (settings.MAIL_BASE_URL, reverse("inkmail:confirm_subscription", args=(self.opt_in_key,), host='mail'))


class ScheduledNewsletterMessage(HashidBaseModel):
    message = models.ForeignKey(Message, blank=True, null=True, on_delete=models.SET_NULL)
    newsletter = models.ForeignKey(Newsletter, blank=True, null=True, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=False)
    complete = models.BooleanField(default=False)

    send_at_date = models.DateField(blank=True, null=True, default=timezone.now)
    send_at_hour = models.IntegerField(blank=True, null=True)
    send_at_minute = models.IntegerField(blank=True, null=True)
    use_local_time = models.BooleanField(default=False)  # if False, use UTC.

    num_scheduled = models.IntegerField(default=0)
    # num_queued = models.IntegerField(default=0) ?
    num_sent = models.IntegerField(default=0)

    def __str__(self):
        if self.send_at_date:
            if self.use_local_time:
                timestamp = "%s %s:%s local time" % (
                    self.send_at_date,
                    self.send_at_hour,
                    self.send_at_minute,
                )
            else:
                timestamp = "%s %s:%s" % (
                    self.send_at_date,
                    self.send_at_hour,
                    self.send_at_minute,
                )
        else:
            timestamp = self.modified_at

        return "%s - %s to %s" % (
            timestamp,
            self.message,
            self.newsletter
        )

    @property
    def recipients(self):
        return self.newsletter.subscriptions.filter(double_opted_in=True, unsubscribed=False)

    @property
    def num_outgoingmessages_success(self):
        return self.outgoingmessage_set.filter(send_success=True).count()

    @property
    def num_outgoingmessages_sent(self):
        return self.outgoingmessage_set.filter(attempt_complete=True).count()

    @property
    def num_outgoingmessages_loved(self):
        return self.outgoingmessage_set.filter(loved=True).count()

    @property
    def num_outgoingmessages_queued(self):
        return self.outgoingmessage_set.count()


class OutgoingMessage(BaseModel):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, blank=True, null=True)
    scheduled_newsletter_message = models.ForeignKey(ScheduledNewsletterMessage, on_delete=models.CASCADE, blank=True, null=True)

    send_at = models.DateTimeField()
    unsubscribe_hash = models.CharField(unique=True, max_length=512, blank=True, null=True)
    delete_hash = models.CharField(unique=True, max_length=512, blank=True, null=True)
    love_hash = models.CharField(unique=True, max_length=512, blank=True, null=True)
    loved = models.BooleanField(default=False)
    loved_at = models.DateTimeField(blank=True, null=True)

    attempt_started = models.BooleanField(default=False)
    retry_if_not_complete_by = models.DateTimeField()
    attempt_complete = models.BooleanField(default=False)
    attempt_completed_at = models.DateTimeField(blank=True, null=True)
    attempt_skipped = models.BooleanField(default=False)
    attempt_count = models.IntegerField(default=0)
    should_retry = models.BooleanField(default=False)
    valid_message = models.BooleanField(default=True)
    send_success = models.NullBooleanField(default=None)

    hard_bounced = models.BooleanField(default=False)
    hard_bounced_at = models.DateTimeField(blank=True, null=True)
    hard_bounce_reason = models.CharField(max_length=254, blank=True, null=True)

    def save(self, *args, **kwargs):
        from utils.factory import Factory
        generate_unsubscribe_hash = False
        if not self.unsubscribe_hash:
            generate_unsubscribe_hash = True
        generate_delete_hash = False
        if not self.delete_hash:
            generate_delete_hash = True
        generate_love_hash = False
        if not self.love_hash:
            generate_love_hash = True

        if not self.retry_if_not_complete_by and self.send_at:
            self.retry_if_not_complete_by = self.send_at + RETRY_IN_TIME

        if self.subscription and not self.person:
            self.person = self.subscription.person

        super(OutgoingMessage, self).save(*args, **kwargs)
        if generate_unsubscribe_hash:
            self.unsubscribe_hash = create_unique_hashid(self.pk, OutgoingMessage, "unsubscribe_hash")
        if generate_delete_hash:
            self.delete_hash = create_unique_hashid(self.pk, OutgoingMessage, "delete_hash")
        if generate_delete_hash:
            self.love_hash = create_unique_hashid(self.pk, OutgoingMessage, "love_hash")
        if generate_unsubscribe_hash or generate_delete_hash or generate_love_hash:
            self.save()

    @property
    def unsubscribe_link(self):
        return "%s%s" % (
            settings.MAIL_BASE_URL,
            reverse("inkmail:unsubscribe", args=(self.unsubscribe_hash, ), host='mail'),
        )

    @property
    def delete_account_link(self):
        return "%s%s" % (
            settings.MAIL_BASE_URL,
            reverse("inkmail:delete_account", args=(self.delete_hash, ), host='mail'),
        )

    @property
    def love_link(self):
        return "%s%s" % (
            settings.MAIL_BASE_URL,
            reverse("inkmail:love_message", args=(self.love_hash, ), host='mail'),
        )

    def render_email_string(self, string_to_render, strip_linebreaks=False, plain_text=False):
        o = Organization.get()
        context = {
            "transactional": self.message.transactional,
            "organization_address": o.address,
            "organization_name": o.name,
        }
        if self.person:
            context.update({
                "first_name": self.person.first_name,
                "last_name": self.person.last_name,
                "email": self.person.email,
            })
        if self.subscription:
            context.update({
                "subscribed_at": self.subscription.subscribed_at,
                "subscription_url": self.subscription.subscription_url,
                "subscribed_from_ip": self.subscription.subscribed_from_ip,
                "has_set_never_unsubscribe": self.subscription.has_set_never_unsubscribe,
                "opt_in_link": self.subscription.opt_in_link,
                "unsubscribe_link": self.unsubscribe_link,
                "love_link": self.love_link,
            })
        if self.message.transactional:
            context.update({
                "transactional_send_reason": self.message.transactional_send_reason,
                "transactional_no_unsubscribe_reason": self.message.transactional_no_unsubscribe_reason,
                "delete_account_link": self.delete_account_link,
            })

        c = Context(context)
        t = Template(string_to_render.replace("\\\n", "\n"))

        parsed_source = t.render(c).encode("utf-8").decode()

        if not strip_linebreaks and not plain_text:
            parsed_source = parsed_source.replace("\r", "\n")
            parsed_source = parsed_source.replace("\n\n", "<br>\n")

        if not plain_text:
            rendered_string = markdown(parsed_source)
        else:
            rendered_string = parsed_source

        rendered_string = rendered_string.replace(u"’", '&rsquo;').replace(u"“", '&ldquo;')
        rendered_string = rendered_string.replace(u"”", '&rdquo;').replace(u"’", "&rsquo;")

        # if plain_text:
        #     rendered_string = bleach.clean(rendered_string, tags=[], strip=True)
        # else:
        #     rendered_string = bleach.clean(rendered_string, strip=True)

        if not strip_linebreaks and not plain_text:
            rendered_string = rendered_string.replace("\r", "\n")
            rendered_string = rendered_string.replace("\n", "<br>\n")
            # rendered_string = rendered_string.replace("\n", "<br>")
            # rendered_string = linebreaks(rendered_string)
        if not plain_text:
            rendered_string = rendered_string.replace("<br><br>", "\n")


        if strip_linebreaks:
            rendered_string = rendered_string.replace("\n", "")
            if rendered_string[-1] == "\n":
                rendered_string = rendered_string[:-1]
        return rendered_string

    def render_subject_and_body(self):
        o = Organization.get()
        subject = self.render_email_string(self.message.subject, strip_linebreaks=True, plain_text=True)

        # Render non-transactional messages
        if not self.message.transactional:
            if self.subscription and self.subscription.newsletter and "unsubscribe_link" not in self.message.body_text_unrendered:
                body_source = "%s\n%s" % (self.message.body_text_unrendered, self.subscription.newsletter.unsubscribe_footer)
            else:
                body_source = self.message.body_text_unrendered
        else:
            if (
                "transactional_send_reason" not in self.message.body_text_unrendered
                or "transactional_no_unsubscribe_reason" not in self.message.body_text_unrendered
                or "delete_account_link" not in self.message.body_text_unrendered
            ):
                body_source = "%s\n%s" % (self.message.body_text_unrendered, o.transactional_footer)
            else:
                body_source = self.message.body_text_unrendered

        text_body = self.render_email_string(body_source, plain_text=True)

        if self.message.body_html_unrendered:
            if not self.message.transactional:
                if self.subscription and self.subscription.newsletter and "unsubscribe_link" not in self.message.body_html_unrendered:  # noqa
                    html_source = "%s\n%s" % (self.message.body_html_unrendered, self.subscription.newsletter.unsubscribe_footer)
                else:
                    html_source = self.message.body_html_unrendered
            else:
                if (
                    "transactional_send_reason" not in self.message.body_html_unrendered
                    or "transactional_no_unsubscribe_reason" not in self.message.body_html_unrendered
                    or "delete_account_link" not in self.message.body_html_unrendered
                ):
                    html_source = "%s\n%s" % (self.message.body_html_unrendered, o.transactional_footer)
                else:
                    html_source = self.message.body_html_unrendered
        else:
            html_source = body_source

        html_body = self.render_email_string(html_source)

        return subject, text_body, html_body

    def send(self):
        tombstone = False
        subject = False
        body = False
        #  print("om.send")
        #  print("not self.attempt_started: %s" % (not self.attempt_started))
        #  print("self.message.transactional is True: %s" % (self.message.transactional is True))
        #  print("self.subscription: %s" % (self.subscription))
        #  print("self.subscription.person is self.person.pk: %s" % (
        #    self.subscription and self.subscription.person.pk == self.person.pk)
        #  )
        #  print("self.subscription.double_opted_in: %s" % (self.subscription and self.subscription.double_opted_in))
        #  print("not self.subscription.unsubscribed: %s" % (self.subscription and not self.subscription.unsubscribed))
        #  print("not self.person.banned: %s" % (not self.person.banned))
        #  print("not self.person.hard_bounced: %s" % (not self.person.hard_bounced))
        if (
            # Don't dogpile.
            not self.attempt_started
            # We're allowed to send this.
            and (
                # Transactional always sends
                self.message.transactional is True
                # Or, you're subscribed.
                or (
                    self.subscription
                    and self.subscription.person.pk == self.person.pk
                    and self.subscription.double_opted_in
                    and not self.subscription.unsubscribed
                )
            )
            # Never send to someone who's banned or hard bounced.
            and not self.person.banned
            and not self.person.hard_bounced
        ):
            try:
                # print("trying")
                # Save about to send metadata
                self.attempt_started = True
                self.attempt_complete = False
                self.retry_if_not_complete_by = timezone.now() + RETRY_IN_TIME
                self.save()

                subject, body, html_body = self.render_subject_and_body()
                # print("subject: %s" % subject)
                # print("body: %s" % body)

                # print(self.message.transactional_send_reason)
                # print(self.message.transactional_no_unsubscribe_reason)
                # print(self.delete_account_link)
                # Final checks to make sure unsubscribe and CAN_SPAM compliance
                if self.message.transactional:
                    if (
                        self.message.transactional_send_reason not in body
                        or self.message.transactional_no_unsubscribe_reason not in body
                        or self.delete_account_link not in body
                    ):
                        self.should_retry = False
                        self.send_success = False
                        self.attempt_complete = True
                        self.attempt_completed_at = timezone.now()
                        self.attempt_count = self.attempt_count + 1
                        self.valid_message = False
                        self.save()
                        if self.message.transactional_send_reason not in body:
                            # print("Transactional message was attempted without transactional_send_reason. Refusing to send.")  # noqa
                            logging.warn("Transactional message was attempted without transactional_send_reason. Refusing to send.")  # noqa
                        if self.message.transactional_no_unsubscribe_reason not in body:
                            # print("Transactional message was attempted without transactional_no_unsubscribe_reason. Refusing to send.")  # noqa
                            logging.warn("Transactional message was attempted without transactional_no_unsubscribe_reason. Refusing to send.")  # noqa
                        if self.delete_account_link not in body:
                            # print("Transactional message was attempted without delete_account_link. Refusing to send.")
                            logging.warn("Transactional message was attempted without delete_account_link. Refusing to send.")
                        return False
                else:
                    if self.unsubscribe_link not in body:
                        self.should_retry = False
                        self.send_success = False
                        self.attempt_complete = True
                        self.attempt_completed_at = timezone.now()
                        self.attempt_count = self.attempt_count + 1
                        self.valid_message = False
                        self.save()
                        # print("Message was attempted without including the unsubscribe_link. Refusing to send.")
                        logging.warn("Message was attempted without including the unsubscribe_link. Refusing to send.")
                        return False
                # print("final checks passsed")

                tombstone, _ = OutgoingMessageAttemptTombstone.objects.get_or_create(
                    send_time=timezone.now(),
                    outgoing_message_pk=self.pk,
                    encrypted_email=self.person.encrypted_email,
                )

                # Send the message.
                from_email = settings.DEFAULT_FROM_EMAIL
                if (
                    self.subscription
                    and self.subscription.newsletter
                    and self.subscription.newsletter.full_from_email
                ):
                    from_email = self.subscription.newsletter.full_from_email

                # print("django_send_mail")
                logging.warn("django_send_mail")
                django_send_mail(subject, body, from_email, [self.person.email, ], html_message=html_body, fail_silently=False)
                self.attempt_complete = True
                self.attempt_count = self.attempt_count + 1
                self.send_success = True
                self.hard_bounced = False
                self.save()
                # print("success")

            except Exception as e:
                print("exception throw")
                import traceback
                traceback.print_exc()
                logging.warn(e)
                # print(e)
                self.attempt_complete = True
                self.attempt_completed_at = timezone.now()
                self.attempt_count = self.attempt_count + 1
                self.send_success = False
                self.save()

                self.hard_bounced = False
                self.send_success = False
                if not tombstone:
                    tombstone, _ = OutgoingMessageAttemptTombstone.objects.get_or_create(
                        send_time=timezone.now(),
                        outgoing_message_pk=self.pk,
                        encrypted_email=self.person.encrypted_email,
                    )

                tombstone.send_success = False
                tombstone.send_error = str(e)
                tombstone.reason = str(e)
                tombstone.attempt_made = True
                tombstone.retry_number = self.attempt_count

            self.save()

            # Log attempt
            if subject is not False:
                tombstone.encrypted_message_subject = encrypt(subject)
            if body is not False:
                tombstone.encrypted_message_body = encrypt(body)
            tombstone.save()
        else:
            if (
                not self.subscription
                or self.subscription.person.pk != self.person.pk
                or not self.subscription.double_opted_in
                or self.subscription.unsubscribed
                or self.person.banned
                or self.person.hard_bounced
            ):
                self.attempt_started = True
                self.attempt_complete = True
                self.attempt_completed_at = timezone.now()
                self.send_success = False
                self.attempt_skipped = True
                self.save()
                # print("logging as skipped.")
                logging.warn("Skipping message.")


class OutgoingMessageAttemptTombstone(BaseModel):
    send_time = models.DateTimeField()
    outgoing_message_pk = models.IntegerField()
    encrypted_email = models.TextField(blank=True, null=True)
    encrypted_message_subject = models.TextField(blank=True, null=True)
    encrypted_message_body = models.TextField(blank=True, null=True)
    send_success = models.NullBooleanField()
    send_error = models.TextField(blank=True, null=True)
    reason = models.CharField(max_length=254, blank=True, null=True)   # Hard_bounce, banned, etc.
    attempt_made = models.NullBooleanField()
    retry_number = models.IntegerField(default=0)


# class Sequence(BaseModel):
#     name = models.CharField(max_length=254, blank=True, null=True)

# class SequenceStep(BaseModel):
#     sequence = models.ForeignKey(SequenceStep, on_delete=models.CASCADE)

#     previous_step = models.ForeignKey(Sequence, blank=True, null=True)
#     wait_time_s = models.IntegerField(blank=True, null=True)

#     step_number = models.IntegerField()

#     send_at = models.DateTimeField()
#     ignore_if_added_after = models.BooleanField()

#     send_message = models.ForeignKey(Message, blank=True, null=True, on_delete=models.CASCADE)
#     add_to_sequennce = models.ForeignKey(Sequence, blank=True, null=True)

# class SequenceSubscription(BaseModel):
#     person = models.ForeignKey(Person, on_delete=models.CASCADE)
#     sequence = models.ForeignKey(Sequence, on_delete=models.CASCADE)

# class SequenceTombstone(BaseModel):
#     person = models.ForeignKey(Person, on_delete=models.CASCADE)
#     sequence = models.ForeignKey(Sequence, on_delete=models.CASCADE)
#     started_at = models.DateTimeField(blank=True, null=True, default=timezone.now)
#     completed_at = models.DateTimeField(blank=True, null=True, default=timezone.now)

# class SequenceStepTombstone(BaseModel):
#     person = models.ForeignKey(Person, on_delete=models.CASCADE)
#     sequence_step = models.ForeignKey(SequenceStep, on_delete=models.CASCADE)
#     started_at = models.DateTimeField(blank=True, null=True, default=timezone.now)
#     completed_at = models.DateTimeField(blank=True, null=True, default=timezone.now)


# class MessageTrigger(BaseModel):
#     message = models.ForeignKey(Message, blank=True, null=True, on_delete=models.SET_NULL)

#     send_after_local_tz = models.DateTimeField(blank=True, null=True, default=timezone.now)
#     send_after_server_tz = models.DateTimeField(blank=True, null=True, default=timezone.now)
#     send_after_message = models.DateTimeField(blank=True, null=True, default=timezone.now)
#     send_after_message = models.DateTimeField(blank=True, null=True, default=timezone.now)
#     subscription = models.ForeignKey(Subscription, blank=True, null=True)

#     # conditions ->  MessageTriggerCondition_set

# class MessageTriggerCondition(BaseModel):
#     message_trigger = models.ForeignKey(MessageTrigger)
#     field = models.CharField(max_length=254)  # subscription.last_last action
#     comparison = models.CharField(max_length=254)   # =, !=, <, >
#     value = models.CharField(max_length=254)  # datetime

#     # action_type = models.CharField(max_length=254)
#     # action_target = models.CharField(max_length=254)
#     # target_message = models.ForeignKey(Message, blank=True, null=True, on_delete=models.SET_NULL)
#     # target_page = models.ForeignKey(Page, blank=True, null=True, on_delete=models.SET_NULL)


# class EmailTombstone(BaseModel):
#     person = models.ForeignKey(Person, on_delete=models.SET_NULL)
#     message = models.ForeignKey(Message, on_delete=models.SET_NULL)
#     trigger = models.ForeignKey(Trigger, on_delete=models.SET_NULL)
#     sent_at = models.DateTimeField(blank=True, null=True, default=timezone.now)

#     encrypted_email = models.TextField(blank=True, null=True)
#     encrypted_message_subject = models.TextField(blank=True, null=True)
#     encrypted_message_body = models.TextField(blank=True, null=True)
