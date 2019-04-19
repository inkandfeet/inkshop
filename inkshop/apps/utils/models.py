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
        return map(lambda field: field.name, cls._model._meta.local_fields)

    def get_data_dict(self):
        data = {}
        for f in self.__class__.get_field_names():
            data[f] = self.getattr(f)
        return data
