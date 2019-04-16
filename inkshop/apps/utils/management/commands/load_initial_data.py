import datetime
import time
import yaml

from django.core.management.base import BaseCommand
from inkmail.models import Newsletter


class Command(BaseCommand):
    help = 'Loads initial data from initial_data.yml'

    def handle(self, *args, **options):
        Newsletter.objects.get_or_create(
            name="The Letter",
            internal_name="letter",
            description="The letters are a weekly serial on authentic living, travel, and humanity, sent from all across the world.",   # noqa
        )
