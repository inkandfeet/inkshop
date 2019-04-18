import datetime
import time
import yaml

from django.core.management.base import BaseCommand
from inkmail.models import Newsletter, Message
from people.models import Person


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
                    if "confirm_subject" in data and "confirm_body" in data:
                        m = Message.objects.get_or_create(name="%s-confirm" % name)
                        m.subject = data["confirm_subject"]
                        m.body_text_unrendered = data["confirm_body"]
                        m.save()

                        n.confirm_message = m

                    if "welcome_subject" in data and "welcome_body" in data:
                        m = Message.objects.get_or_create(name="%s-welcome" % name)
                        m.subject = data["welcome_subject"]
                        m.body_text_unrendered = data["welcome_body"]
                        m.save()

                        n.welcome_message = m
                    n.save()

            if "troll_emails" in data:
                for e in data["troll_emails"]:
                    p = Person.objects.get_or_create(email=e)
                    p.mark_troll()

            if "banned_emails" in data:
                for e in data["banned_emails"]:
                    p = Person.objects.get_or_create(email=e)
                    p.ban()
