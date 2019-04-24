import datetime
import time
import yaml

from django.core.management.base import BaseCommand
from inkmail.models import Newsletter, Message, Organization
from people.models import Person
from utils.encryption import lookup_hash

MESSAGE_FIELDS = [
    "confirm_subject",
    "confirm_body",
    "welcome_subject",
    "welcome_body",
]


class Command(BaseCommand):
    help = 'Loads initial data from initial_data.yml'

    def handle(self, *args, **options):
        with open("initial_data.yml", encoding='utf8') as f:
            data = yaml.safe_load(f)
            print(data)

            if "organization" in data:
                o = Organization.get()
                for k, v in data["organization"]:
                    setattr(o, k, v)
                o.save()

            if "newsletters" in data:
                for name, info in data["newsletters"].items():
                    n, _ = Newsletter.objects.get_or_create(
                        internal_name=info["internal_name"]
                    )
                    for k, v in info.items():
                        if k not in MESSAGE_FIELDS:
                            setattr(n, k, v)

                    if "confirm_subject" in info and "confirm_body" in info:
                        m, _ = Message.objects.get_or_create(name="%s-confirm" % name)
                        m.subject = info["confirm_subject"]
                        m.body_text_unrendered = info["confirm_body"]
                        m.save()

                        n.confirm_message = m

                    if "welcome_subject" in info and "welcome_body" in info:
                        m, _ = Message.objects.get_or_create(name="%s-welcome" % name)
                        m.subject = info["welcome_subject"]
                        m.body_text_unrendered = info["welcome_body"]
                        m.save()

                        n.welcome_message = m
                    n.save()

            if "troll_emails" in data:
                for e in data["troll_emails"]:
                    ee = lookup_hash(e)
                    p, _ = Person.objects.get_or_create(hashed_email=ee)
                    p.mark_troll()

            if "banned_emails" in data:
                for e in data["banned_emails"]:
                    ee = lookup_hash(e)
                    p, _ = Person.objects.get_or_create(hashed_email=ee)
                    p.ban()
