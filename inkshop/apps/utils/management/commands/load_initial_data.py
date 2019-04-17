import datetime
import time
import yaml

from django.core.management.base import BaseCommand
from inkmail.models import Newsletter
from people.models import Person


class Command(BaseCommand):
    help = 'Loads initial data from initial_data.yml'

    def handle(self, *args, **options):
        with open("initial_data.yml") as f:
            data = yaml.safe_load(f)
            print(data)

            if "newsletters" in data:
                for name, info in data["newsletters"].items():
                    Newsletter.objects.get_or_create(
                        **info
                    )

            if "troll_emails" in data:
                for e in data["troll_emails"]:
                    p = Person.objects.get_or_create(email=e)
                    p.mark_troll()

            if "banned_emails" in data:
                for e in data["banned_emails"]:
                    p = Person.objects.get_or_create(email=e)
                    p.ban()
