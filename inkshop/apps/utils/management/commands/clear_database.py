import datetime
import time
import yaml

from django.core.management.base import BaseCommand
from django.conf import settings
from inkmail.models import Newsletter, Subscription
from people.models import Person


class Command(BaseCommand):
    help = 'Resets the dev database'

    def add_arguments(self, parser):
        parser.add_argument('--confirm', type=bool)

    def handle(self, *args, **options):
        if hasattr(settings, "IS_LIVE") and settings.IS_LIVE:
            print("In production (IS_LIVE=True).  Refusing to run.")
            return

        if "confirm" not in options:
            print("Missing --confirm")
            return

        Newsletter.objects.all().delete()
        Subscription.objects.all().delete()
        Person.objects.all().delete()
