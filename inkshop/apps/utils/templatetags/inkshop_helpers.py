from django import template
import json
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="json")
def json_filter(value):
    return mark_safe(json.dumps(value))


@register.filter(name="times")
def times(number):
    return range(1, number + 1)


@register.filter(name='dict_key')
def dict_key(d, k):
    if d and (hasattr(d, k) or k in d):
        if (hasattr(d, k)):
            return getattr(d, k)

        return d[k]
    return None
