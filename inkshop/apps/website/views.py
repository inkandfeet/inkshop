import logging
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404

from annoying.decorators import render_to, ajax_request
from website.models import Page, Post, Resource

CACHED_PAGES = {}
CACHED_RESOURCES = {}
CACHABLE_RESOURCE_TYPES = [

]


@render_to("website/home.html")
def home(request):
    return locals()


def page_or_post(request, page_slug):
    if page_slug in CACHED_PAGES:
        content = CACHED_PAGES[page_slug]
    else:
        try:
            page = Page.objects.get(slug__iexact=page_slug)
            content = page.rendered
        except:
            try:
                post = Post.objects.get(slug__iexact=page_slug)
                content = post.rendered
            except Exception:
                if not settings.DEBUG:
                    raise Http404("Page does not exist")
                raise
        CACHED_PAGES[page_slug] = content

    response = HttpResponse(content)
    response['Content-Length'] = len(content)
    return response


def resource(request, resource_slug):
    if settings.DEBUG:
        CACHED_RESOURCES = {}  # noqa

    if resource_slug in CACHED_RESOURCES:
        return CACHED_RESOURCES[resource_slug]
    else:
        try:
            resource = Resource.objects.get(name__iexact=resource_slug)
            content = resource.content
        except:
            if not settings.DEBUG:
                raise Http404("File does not exist")
            raise

    if resource.mime_type:
        response = HttpResponse(content, content_type=resource.mime_type)
        response['Content-Type'] = resource.mime_type
    else:
        response = HttpResponse(content)
    response['Content-Length'] = len(content)

    CACHED_RESOURCES[resource_slug] = response
    return response
