import logging
from django.forms import ModelForm, CharField, TextInput
from inkmail.models import ScheduledNewsletterMessage, Message, OutgoingMessage, Newsletter, Subscription
from inkmail.models import Organization
from django.forms import modelformset_factory


class ScheduledNewsletterMessageForm(ModelForm):
    class Meta:
        model = ScheduledNewsletterMessage
        fields = [
            "message",
            "newsletter",
            "enabled",
            "complete",
            "send_at_date",
            "send_at_hour",
            "send_at_minute",
            "use_local_time",
            "num_scheduled",
            "num_sent",
        ]


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = [
            "name",
            "subject",
            "body_text_unrendered",
            "body_html_unrendered",
            "reward_image",
            "transactional",
            "transactional_send_reason",
            "transactional_no_unsubscribe_reason",
        ]


class OutgoingMessageForm(ModelForm):
    class Meta:
        model = OutgoingMessage
        fields = [
            "person",
            "message",
            "subscription",
            "scheduled_newsletter_message",
            "send_at",
            "unsubscribe_hash",
            "delete_hash",
            "love_hash",
            "loved",
            "loved_at",
            "attempt_started",
            "retry_if_not_complete_by",
            "attempt_complete",
            "attempt_count",
            "should_retry",
            "valid_message",
            "send_success",
            "hard_bounced",
            "hard_bounce_reason",
        ]


class NewsletterForm(ModelForm):
    class Meta:
        model = Newsletter
        fields = [
            "name",
            "internal_name",
            "description",
            "from_email",
            "from_name",
            "unsubscribe_footer",
            "confirm_message",
            "welcome_message",
            "unsubscribe_if_no_hearts_after_days",
            "unsubscribe_if_no_hearts_after_days_num",
            "unsubscribe_if_no_hearts_after_messages",
            "unsubscribe_if_no_hearts_after_messages_num",
        ]


class SubscriptionForm(ModelForm):
    class Meta:
        model = Subscription
        fields = [
            "person",
            "newsletter",
            "subscribed_at",
            "subscription_url",
            "subscribed_from_ip",
            "was_imported",
            "was_imported_at",
            "import_source",
            "double_opted_in",
            "double_opted_in_at",
            "has_set_never_unsubscribe",
            "unsubscribed",
            "unsubscribed_at",
        ]


class OrganizationForm(ModelForm):
    class Meta:
        model = Organization
        fields = [
            "name",
            "address",
            "transactional_footer",
            "favicon",
            "robots_txt",
        ]
