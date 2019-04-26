import logging
from django.forms import ModelForm, CharField, TextInput
from inkmail.models import ScheduledNewsletterMessage, Message, OutgoingMessage, Newsletter, Subscription
from inkmail.models import Organization
from django.forms import modelformset_factory


class ScheduledNewsletterMessageForm(ModelForm):
    class Meta:
        model = ScheduledNewsletterMessage


class MessageForm(ModelForm):
    class Meta:
        model = Message


class OutgoingMessageForm(ModelForm):
    class Meta:
        model = OutgoingMessage


class NewsletterForm(ModelForm):
    class Meta:
        model = Newsletter


class SubscriptionForm(ModelForm):
    class Meta:
        model = Subscription
