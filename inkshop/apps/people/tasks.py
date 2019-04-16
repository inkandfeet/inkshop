import json
import requests

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from celery.task import task


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@task(name="log_signup_attempt", acks_late=True, queue='logging',)
def log_signup_attempt(data, ip, successful):
    # LoggedSignupAttempt.objects.create(
    #     # attempt_full_name=data["full_name"],
    #     attempt_email=data["email"],
    #     attempt_password=hexlify(encrypt(settings.ACCESS_LOG_KEY, data["password"].encode('utf8'))).decode(),
    #     # attempt_terms=data["agreed_to_terms"],
    #     attempting_ip=ip,
    #     successful=successful
    # )
    pass
