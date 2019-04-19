import datetime
from django.utils import timezone
from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(db_index=True, blank=True, null=True, default=timezone.now)
    modified_at = models.DateTimeField(blank=True, null=True, auto_now=True)

    class Meta:
        abstract = True

    @classmethod
    def get_field_names(cls):
        # Uses new recommended method:
        # https://docs.djangoproject.com/en/2.2/ref/models/meta/#migrating-from-the-old-api
        return [
            f.name
            for f in cls._meta.get_fields()
            if not f.is_relation
            or f.one_to_one
            or (f.many_to_one and f.related_model)
        ]

    def get_data_dict(self):
        data = {}
        for f in self.__class__.get_field_names():
            data[f] = getattr(self, f)
        return data
