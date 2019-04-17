import datetime
import time
import yaml

from django.core.management.base import BaseCommand
from inkmail.models import Newsletter
from people.models import BlacklistedEmail


class Command(BaseCommand):
    help = 'Loads initial data from initial_data.yml'

    def handle(self, *args, **options):
        with open("initial_data.yml") as f:
            data = yaml.safe_load(f)
            print(data)

            if "newsletters" in data:
                for name, info in data["newsletters"].items():
                    n = Newsletter.objects.get_or_create(
                        **info
                    )
            if "blacklist_emails" in data:
                for e in data["blacklisted_emails"]:
                    BlacklistedEmail.objects.get_or_create(email=e)
