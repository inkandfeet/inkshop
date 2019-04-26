import datetime
import jwt
from django.utils import timezone
from django.db import models
from django.conf import settings
from utils.encryption import create_unique_hashid
from django.utils.functional import cached_property


class DataDictMixin(object):

    @classmethod
    def get_field_names(cls):
        # Uses new recommended method:
        # https://docs.djangoproject.com/en/2.2/ref/models/meta/#migrating-from-the-old-api
        fields = []
        for f in cls._meta.get_fields():
            if (
                not hasattr(f, "storage")
                and (
                    not f.is_relation
                    or f.one_to_one
                    or (f.many_to_one and f.related_model)
                )
            ):
                fields.append(f.name)
        return fields

    def get_data_dict(self, instance=None):
        data = {}
        if not instance:
            instance = self
        for f in instance.__class__.get_field_names():
            if hasattr(getattr(instance, f).__class__, "get_field_names"):
                val = self.get_data_dict(instance=getattr(instance, f))
            else:
                val = getattr(instance, f)
            data[f] = val
        return data


class BaseModel(DataDictMixin, models.Model):
    created_at = models.DateTimeField(db_index=True, blank=True, null=True, default=timezone.now)
    modified_at = models.DateTimeField(blank=True, null=True, auto_now=True)

    class Meta:
        abstract = True


class HashidBaseModel(DataDictMixin, models.Model):
    created_at = models.DateTimeField(db_index=True, blank=True, null=True, default=timezone.now)
    modified_at = models.DateTimeField(blank=True, null=True, auto_now=True)

    class Meta:
        abstract = True

    hashid = models.CharField(max_length=254, blank=True, null=True, db_index=True)

    def save(self, *args, **kwargs):
        create_hashid = False
        if not self.hashid:
            create_hashid = True
        super(HashidBaseModel, self).save(*args, **kwargs)

        if create_hashid:
            self.hashid = create_unique_hashid(self.pk, self.__class__, "hashid")
            self.save()


class HasJWTBaseModel(BaseModel):
    inkid = models.CharField(blank=True, null=True, max_length=512, unique=True, db_index=True, editable=False)
    salted_inkid = models.CharField(blank=True, null=True, max_length=512, unique=True, db_index=True, editable=False)
    api_jwt_cached = models.CharField(blank=True, null=True, max_length=512, unique=True, editable=False)

    class Meta:
        abstract = True

    def regenerate_api_jwt(self):
        self.api_jwt_cached = jwt.encode({
            'inkid': self.inkid,
            'version': 1,
            'user_type': self.user_type,

        }, settings.JWT_SECRET, algorithm='HS256').decode()

        return self.api_jwt_cached

    @cached_property
    def api_jwt(self):
        if not self.api_jwt_cached:
            self.api_jwt_cached = self.regenerate_api_jwt()
            self.save()

        return self.api_jwt_cached

    @cached_property
    def events(self):
        from events.models import Event
        return Event.objects.filter(creator=self.inkid)
