from django.template import Origin, TemplateDoesNotExist
from django.template.loaders.base import Loader as BaseLoader
from django.conf import settings

from website.models import Template

TEMPLATE_CACHE = {}
TEMPLATE_CACHE_UPDATED_AT = None

TEMPLATE_NORMAL = """{%% extends "base.html" %%}{%% load static %%}
{%% block nav %%}%(nav)s{%% endblock %%}
{%% block content %%}%(content)s{%% endblock %%}
{%% block html_extra_classes %%}%(html_extra_classes)s{%% endblock %%}
{%% block footer %%}%(footer)s{%% endblock %%}
{%% block css %%}%(css)s{%% endblock %%}
{%% block js %%}%(js)s{%% endblock %%}
"""

TEMPLATE_WITH_BODY_OVERRIDE = """{%% extends "base.html" %%}{%% load static %%}
{%% block html_extra_classes %%}%(html_extra_classes)s{%% endblock %%}
{%% block body %%}%(body_override)s{%% endblock %%}
{%% block css %%}%(css)s{%% endblock %%}
{%% block js %%}%(js)s{%% endblock %%}
"""

TEMPLATE_WITH_EVERYTHING_OVERRIDE = """{%% extends "base.html" %%}{%% load static %%}
{%% block everything_override %%}%(everything_override)s{%% endblock %%}
"""


class Loader(BaseLoader):

    def get_template_sources(self, template_name, template_dirs=None):
        yield Origin(
            name=template_name,
            template_name=template_name,
            loader=self,
        )

    def get_contents(self, origin, **kwargs):
        global TEMPLATE_CACHE
        if settings.DEBUG or (hasattr(settings, "TEST_MODE") and settings.TEST_MODE):
            TEMPLATE_CACHE = {}  # noqa 
        if True or origin.template_name not in TEMPLATE_CACHE.keys():
            kwarg_context = None
            if "context" in kwargs:
                kwarg_context = kwargs["context"].copy()
                del kwargs["context"]

            try:
                t = Template.objects.get(name__exact=origin.template_name, **kwargs)
            except:
                raise TemplateDoesNotExist(origin.template_name)

            context = t.context
            if kwarg_context:
                context.update(**kwarg_context)

            if t.body_override:
                template_string = TEMPLATE_WITH_BODY_OVERRIDE % context
            elif t.everything_override:
                template_string = TEMPLATE_WITH_EVERYTHING_OVERRIDE % context
            else:
                template_string = TEMPLATE_NORMAL % context

            return template_string
            # TEMPLATE_CACHE[origin.template_name] = template_string

        # return TEMPLATE_CACHE[origin.template_name]
