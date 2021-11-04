from django.core.management.base import BaseCommand
from inkdots.models import Event


class Command(BaseCommand):
    help = 'Downloads the entire events table, as json.'

    # def add_arguments(self, parser):
    #     parser.add_argument('--confirm', type=bool)

    def handle(self, *args, **options):
        print("[")
        num_events = Event.objects.all().count()
        counter = 0
        for e in Event.objects.all().order_by("created_at"):
            counter += 1
            if counter == num_events:
                print("%s" % e.to_json())
            else:
                print("%s," % e.to_json())
        print("]")
        print("\n")
        print("\n")
        print("\n")
        print("\n")
        print("\n")
        print("\n")
