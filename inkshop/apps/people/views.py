from base64 import b64decode
import datetime
import json
import logging
import time

from django.conf import settings
from django.core.mail import mail_admins
from django.contrib.auth import authenticate, login
from django.db import IntegrityError
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from annoying.decorators import render_to, ajax_request
from utils.factory import Factory


CORRECT_PASSWORD_STRING = "!!CORRECT!!InkshopSalt"

# TODO:
# Sign up
# Reset Password
# Unsubscribe
# Delete account
# GDPR


@render_to("people/home.html")
def home(request):
    return locals()


@render_to("people/email_confirmation.html")
def confirm_email(request, email_key):
    u = User.objects.get(email_confirm_key=email_key)
    u.email_verified = True
    u.save()
    email_confirmed = True
    firebase_put("users/%s/internal/email_verified" % u.inkid, {".value": True})
    return locals()


@render_to("people/opt_out.html")
def opt_out(request, reader_opt_out_key):
    s = Reader.objects.get(opt_out_key=reader_opt_out_key)
    s.opted_out_of_email = True
    s.save()
    return locals()


@ajax_request
@csrf_exempt
def user_authenticate(request):
    resp = {
        "success": False,
    }
    data = None
    if request.body:
        data = json.loads(request.body.decode('utf-8'))
    if data and "email" in data and "password" in data:
        data["email"] = data["email"].lower()
        user = authenticate(username=data["email"], password=data["password"])
        if user is not None and user.is_active and (
            "gc" not in data or data["gc"] is False or user.is_staff
        ):
            login(request, user)
            resp = user.info
            resp["success"] = True

    if resp["success"]:
        password = CORRECT_PASSWORD_STRING
    else:
        password = data["password"]
    log_access_attempt.delay(
        data["email"],
        password,
        request.META["REMOTE_ADDR"],
        resp["success"],
    )

    return resp


@ajax_request
@csrf_exempt
def firebase_user_create(request):
    # Authenticates a widget visitor, and populates the data for them.
    resp = {
        "success": False,
    }

    # Authenticate and prove that this is coming from firebase.
    # if "Authorization"

    # Verify body.
    data = None
    if request.body:
        data = json.loads(request.body.decode('utf-8'))

    if data and "email" in data:
        resp["success"] = True

    # handle_event.delay(event)

    return resp


@ajax_request
@csrf_exempt
def change_password(request):

    resp = {
        "success": False,
    }
    data = None
    if request.body:
        data = json.loads(request.body.decode('utf-8'))

    if data and "inkid" in data and "api_jwt" in data and "password" in data:
        user = User.objects.get(inkid=data["inkid"])
        assert user.api_jwt == data["api_jwt"]
        user.set_password(data["password"])
        user.must_reset_password = False

        if user.migrated_user:
            user.has_signed_in = True

        user.save()
        resp["success"] = True

    log_password_attempt.delay(
        data["inkid"],
        request.META["REMOTE_ADDR"],
        resp["success"],
    )

    return resp


@ajax_request
@csrf_exempt
def reset_password(request):

    resp = {
        "success": False,
        "error": "",
    }
    data = None
    if request.body:
        data = json.loads(request.body.decode('utf-8'))

    try:
        if data and "email" in data:
            if User.objects.filter(email__iexact=data["email"]).count() != 1:
                resp["error"] = "No account with that email."
            else:
                user = User.objects.get(email__iexact=data["email"])
                user.send_reset_key()
                resp["success"] = True

        log_password_attempt.delay(
            data["email"],
            request.META["REMOTE_ADDR"],
            resp["success"],
        )
    except:
        import traceback
        traceback.print_exc()
        pass

    return resp


@render_to("people/password_reset_confirmation.html")
def confirm_reset(request, email_key):
    saved = False
    try:
        u = User.objects.get(reset_key=email_key)
        a = u

        if request.method == "POST":
            if request.POST["new_password"]:
                u.set_password(request.POST["new_password"])
                u.save()
                a = u
                saved = True

        else:
            pass
    except:
        pass
    return locals()


@ajax_request
@csrf_exempt
def check_new_account(request):

    resp = {
        "success": False,
        "newAccount": True,
    }
    data = None
    if request.body:
        data = json.loads(request.body.decode('utf-8'))

    try:
        if data and "email" in data:
            resp["success"] = True

            User.objects.get(email__iexact=data["email"])
            resp["newAccount"] = False

            log_account_check_attempt.delay(
                data["email"],
                request.META["REMOTE_ADDR"],
                resp["success"],
            )
    except:
        import traceback
        traceback.print_exc()
        pass

    return resp
