import pickle
from django.db import models
from django.conf import settings
from django.utils.functional import cached_property
from django.utils import timezone

from utils.encryption import encrypt_bytes, decrypt_bytes


class HistoricalEvent(models.Model):
    """
    This table is a sink for historical events only.
    It should never be queried unless there's some kind of need from a forensics perspective.
    """

    created_at = models.DateTimeField(blank=True, null=True, default=timezone.now)
    modified_at = models.DateTimeField(blank=True, null=True, auto_now=True)
    event_type = models.CharField(max_length=254, blank=True, null=True)
    event_creator_type = models.CharField(max_length=254, blank=True, null=True)
    event_creator_pk = models.IntegerField(blank=True, null=True)
    encrypted_json_event_data = models.TextField(blank=True, null=True)

    @property
    def event_data(self):
        if not hasattr(self, "_decrypted_event_data"):
            self._decrypted_event_data = pickle.loads(decrypt_bytes(self.encrypted_json_event_data))
        return self._decrypted_event_data

    @event_data.setter
    def event_data(self, value):
        self.encrypted_json_event_data = encrypt_bytes(pickle.dumps(value))

    @classmethod
    def expand_kwargs_to_instance_and_event_data(cls, **kwargs):
        from inkmail.models import Message, Newsletter, Subscription, OutgoingMessage
        from people.models import Person
        instance_data = {}
        event_data = {}

        for k, v in kwargs.items():
            if k == "person" and isinstance(v, Person):
                instance_data["event_creator_type"] = "person"
                instance_data["event_creator_pk"] = kwargs["person"].pk
                event_data["person"] = kwargs["person"].get_data_dict()
            elif k == "message" and isinstance(v, Message):
                event_data["message"] = kwargs["message"].get_data_dict()
            elif k == "subscription" and isinstance(v, Subscription):
                event_data["subscription"] = kwargs["subscription"].get_data_dict()
            elif k == "newsletter" and isinstance(v, Newsletter):
                event_data["newsletter"] = kwargs["newsletter"].get_data_dict()
            elif k == "outgoingmessage" and isinstance(v, OutgoingMessage):
                event_data["outgoingmessage"] = kwargs["outgoingmessage"].get_data_dict()
            elif k == "event_type":
                instance_data["event_type"] = v
            else:
                event_data[k] = v
        return instance_data, event_data

    @classmethod
    def log(cls, *args, **kwargs):
        instance_data, event_data = cls.expand_kwargs_to_instance_and_event_data(**kwargs)
        instance = cls.objects.create(**instance_data)
        instance.event_data = event_data
        instance.save()
