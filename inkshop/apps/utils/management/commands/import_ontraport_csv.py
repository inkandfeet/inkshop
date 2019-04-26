import datetime
from dateutil import tz
from dateutil.parser import parse

ET = tz.gettz('US/Eastern')
CT = tz.gettz('US/Central')
MT = tz.gettz('US/Mountain')
PT = tz.gettz('US/Pacific')

us_tzinfos = {'CST': CT, 'CDT': CT,
              'EST': ET, 'EDT': ET,
              'MST': MT, 'MDT': MT,
              'PST': PT, 'PDT': PT}

import time
import csv

from django.core.management.base import BaseCommand
from inkmail.models import Newsletter, Message
from people.models import Person
from utils.encryption import lookup_hash


class Command(BaseCommand):
    help = 'Imports mailing list data'

    def add_arguments(self, parser):
        parser.add_argument('--hard_bounce', type=str)
        parser.add_argument('--unsubscribed', type=str)
        parser.add_argument('--subscribers', type=str)
        parser.add_argument('--newsletter', type=str)

    def handle(self, *args, **options):
        print(options)
        Newsletter.objects.get(internal_name=options["newsletter"])
        if "hard_bounce" in options and options["hard_bounce"]:
            with open(options["hard_bounce"], encoding='utf-8') as hard_f:
                reader = csv.reader(hard_f)
                row_num = 0
                for row in reader:
                    if row_num != 0 and len(row) > 2:
                        # print(row)
                        # index = 0
                        # for c in row:
                        #     print("%s %s" % (index, c))
                        #     index += 1

                        first_name = row[1]
                        last_name = row[2]
                        email = row[3]
                        time_zone = row[63]

                        status = row[21]
                        # 1-17-2019 02:42 AM PDT
                        # print(row[58])
                        # subscribed_at = parser.parse(row[58])
                        # Stupid ontraport's invented US-centric timezones
                        # date_portion = " ".join(row[58].split(" ")[:-1])
                        # tz_portion = row[58].split(" ")[-1]
                        subscribed_at = parse(row[58], tzinfos=us_tzinfos)
                        hard_bounced_at = parse(row[61], tzinfos=us_tzinfos)
                        # subscribed_at = datetime.datetime.strptime(row[58], "%m-%d-%Y %H:%M %p")

                        subscribe_ip = row[62]

                        # print(first_name)
                        # print(last_name)
                        print("Hard bounced: %s at %s" % (email, hard_bounced_at))
                        # print(status)
                        # print(subscribed_at)
                        # print(subscribe_ip)
                        Newsletter.import_subscriber(
                            import_source="csv-hard-bounce-%s" % options["hard_bounce"],
                            email=email,
                            subscribed_at=subscribed_at,
                            subscription_url="https://inkandfeet.com/letter",
                            double_opted_in=False,
                            double_opted_in_at=subscribed_at,
                            hard_bounced=True,
                            hard_bounced_at=hard_bounced_at,
                            hard_bounced_reason="Unsubscribed in previous system.",
                            first_name=first_name,
                            last_name=last_name,
                            subscription_ip=subscribe_ip,
                            time_zone=time_zone,
                            newsletter_name=options["newsletter"],
                            overwrite=False,
                        )

                        # Hard-coded columns for bootstrap
                        # 1 first_name
                        # 2 last_name
                        # 3 email
                        # 22 status
                        # 58 subscribed_at

                    row_num += 1

        if "subscribers" in options and options["subscribers"]:
            with open(options["subscribers"], encoding='utf-8') as f:
                reader = csv.reader(f)
                row_num = 0
                for row in reader:
                    # print(row)
                    # index = 0
                    # for c in row:
                    #     print("%s %s" % (index, c))
                    #     index += 1
                    if row_num != 0 and len(row) > 2:

                        first_name = row[1]
                        last_name = row[2]
                        email = row[3]
                        time_zone = row[63]

                        status = row[21]
                        # 1-17-2019 02:42 AM PDT
                        # print(row[58])
                        # subscribed_at = parser.parse(row[58])
                        # Stupid ontraport's invented US-centric timezones
                        # date_portion = " ".join(row[58].split(" ")[:-1])
                        # tz_portion = row[58].split(" ")[-1]
                        subscribed_at = parse(row[58], tzinfos=us_tzinfos)
                        # subscribed_at = datetime.datetime.strptime(row[58], "%m-%d-%Y %H:%M %p")

                        subscribe_ip = row[62]

                        # print(first_name)
                        # print(last_name)
                        # print(email)
                        # print(status)
                        # print(subscribed_at)
                        # print(subscribe_ip)

                        # Double-check
                        if status == "Double Opt-In" or status == "Single Opt-in":
                            # print("do import")
                            Newsletter.import_subscriber(
                                import_source="csv-subscribers-%s" % options["subscribers"],
                                email=email,
                                subscribed_at=subscribed_at,
                                subscription_url="https://inkandfeet.com/letter",
                                double_opted_in=True,
                                double_opted_in_at=subscribed_at,
                                first_name=first_name,
                                last_name=last_name,
                                subscription_ip=subscribe_ip,
                                time_zone=time_zone,
                                newsletter_name=options["newsletter"],
                                overwrite=False,
                            )
                            print(email)
                        else:
                            print("Skipping %s - %s" % (email, status))
                            # print(status)

                        # Hard-coded columns for bootstrap
                        # 1 first_name
                        # 2 last_name
                        # 3 email
                        # 22 status
                        # 58 subscribed_at

                    row_num += 1
