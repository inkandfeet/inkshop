import os
import json
import sys
import requests


def do_purge():
    if "CLOUDFLARE_API_KEY" not in os.environ:
        raise Exception("Missing CLOUDFLARE_API_KEY.")
    if "CLOUDFLARE_EMAIL" not in os.environ:
        raise Exception("Missing CLOUDFLARE_EMAIL.")

    domains = sys.argv[1:]

    api_key = os.environ["CLOUDFLARE_API_KEY"]
    email = os.environ["CLOUDFLARE_EMAIL"]

    # Get the zone from cloudflare
    headers = {
        "X-Auth-Key": api_key,
        "X-Auth-Email": email,
        "Content-Type": "application/json",
    }
    url = "https://api.cloudflare.com/client/v4/zones/"
    if len(domains) > 0:
        for d in domains:
            params = {
                "name": d.replace("https://", "").replace("http://", ""),
                "status": "active",
                "page": 1,
                "per_page": 20,
                "order": "status",
                "direction": "desc",
                "match": "all",
            }

            r = requests.get(url, params=params, headers=headers)

            if not r.status_code == 200:
                print("Error at Cloudflare:")
                print(r.json())
                raise Exception("Cache not purged.")

            if "result" in r.json() and len(r.json()["result"]) == 1:
                zone_id = r.json()["result"][0]["id"]
                url = "%s%s/purge_cache" % (url, zone_id)

                data = {
                    "purge_everything": True
                }

                r = requests.delete(url, data=json.dumps(data), headers=headers)

                if not r.status_code == 200:
                    print(r.status_code)
                    print(r.json())
                    raise Exception("Error purging cache: %s" % r.json()["errors"][0]["message"])
            else:
                print("Either there isn't a record at cloudflare with domain %s, or there are several." % d)
                raise Exception("Cache not purged.")
            print("%s purged" % d)
        print("Cache purged.")
    else:
        print("No domains specified. Try `python purge_cloudflare.py example.com` or similar")


if __name__ == '__main__':
    do_purge()
