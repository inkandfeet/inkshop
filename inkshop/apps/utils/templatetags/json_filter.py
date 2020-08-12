from django import template
import json
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name="json")
def json_filter(value):
    return mark_safe(json.dumps(value))