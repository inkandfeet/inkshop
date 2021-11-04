import hashlib
import json
import time

from django.db import models
from utils.models import BaseModel

EVENT_SALT = "19mca9zj93qjliAJdlkj"


class Action(BaseModel):
    person = models.ForeignKey('people.Person', on_delete=models.CASCADE)
    action_type = models.CharField(max_length=254)
    action_target = models.CharField(max_length=254)
    target_message = models.ForeignKey('inkmail.Message', blank=True, null=True, on_delete=models.SET_NULL)
    target_page = models.ForeignKey('website.Page', blank=True, null=True, on_delete=models.SET_NULL)


class MessageHeart(BaseModel):
    person = models.ForeignKey('people.Person', on_delete=models.CASCADE)
    message = models.ForeignKey('inkmail.Message', blank=True, null=True, on_delete=models.SET_NULL)


class Device(BaseModel):
    fingerprint = models.CharField(max_length=255, db_index=True)
    hardware_family = models.CharField(max_length=255, blank=True, null=True)
    hardware_brand = models.CharField(max_length=255, blank=True, null=True)
    os = models.CharField(max_length=255, blank=True, null=True)
    browser = models.CharField(max_length=255, blank=True, null=True)
    width = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    is_mobile = models.NullBooleanField(db_index=True, blank=True, null=True)
    is_tablet = models.NullBooleanField(blank=True, null=True)
    is_desktop = models.NullBooleanField(db_index=True, blank=True, null=True)
    is_touch_capable = models.NullBooleanField(blank=True, null=True)
    is_bot = models.NullBooleanField(blank=True, null=True)


class PageHeart(BaseModel):
    person = models.ForeignKey('people.Person', on_delete=models.CASCADE, blank=True, null=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, blank=True, null=True)
    page = models.ForeignKey('website.Page', blank=True, null=True, on_delete=models.SET_NULL)


class PageView(BaseModel):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    page = models.ForeignKey('website.Page', blank=True, null=True, on_delete=models.SET_NULL)
    url = models.TextField(blank=True, null=True)


class Event(BaseModel):
    event_type = models.CharField(max_length=254)
    base_url = models.CharField(max_length=512)
    querystring = models.TextField()
    full_url = models.TextField()
    data = models.TextField(blank=True, null=True)
    request_ip = models.CharField(max_length=50)
    request_ua = models.CharField(max_length=512)
    hashid = models.CharField(max_length=512, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.hashid:
            self.hashid = hashlib.md5(("%s%s" % (self.request_ip, self.request_ua)).encode('utf-8')).hexdigest()[:511]
        super(Event, self).save(*args, **kwargs)

    def to_json(self):
        return json.dumps({
            "created_at": self.created_at.timestamp() * 1000,
            "created_at_friendly": "%s" % self.created_at,
            "event_type": self.event_type,
            "base_url": self.base_url,
            "querystring": self.querystring,
            "full_url": self.full_url,
            "data": self.data,
            "request_ip": self.request_ip,
            "request_ua": self.request_ua,
            "hashid": self.hashid,
        })
