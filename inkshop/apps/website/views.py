import re
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404, HttpResponseNotModified

from annoying.decorators import render_to, ajax_request
from django.template.loader import render_to_string
from inkmail.models import Organization
from website.models import Page, Post, Resource

CACHED_PAGES = {}
CACHED_RESOURCES = {}
CACHABLE_RESOURCE_TYPES = [

]
RESOURCE_HASHES = {}
ALL_RESOURCES = []


# Via https://stackoverflow.com/a/15448887/173933
def multiple_replace(string, rep_dict):
    if len(rep_dict.keys()) and string != "":
        pattern = re.compile("|".join([re.escape(k) for k in sorted(rep_dict, key=len, reverse=True)]), flags=re.DOTALL)
        return pattern.sub(lambda x: rep_dict[x.group(0)], string)
    else:
        return string


@render_to("website/home.html")
def home(request):
    o = Organization.get()
    return locals()


def sitemap(request):
    if request.is_secure:
        domain = "https://%s/" % request.META['HTTP_HOST']
    else:
        domain = "http://%s/" % request.META['HTTP_HOST']

    pages = Page.objects.filter(published=True, private=False).order_by("-created_at")
    posts = Post.objects.filter(published=True, private=False).order_by("-publish_date", "-created_at")
    content_type = "text/xml"
    content = render_to_string("website/sitemap.xml", locals())
    return HttpResponse(content, content_type=content_type)


def robots(request):
    o = Organization.get()
    if o.robots_txt:
        return HttpResponse(o.robots_txt, content_type="text/plain")
    raise Http404("File does not exist")


def favicon(request):
    o = Organization.get()
    if o.favicon:
        return resource(request, o.favicon.name)
    raise Http404("File does not exist")


def page_or_post(request, page_slug=None):
    global CACHED_PAGES
    global RESOURCE_HASHES
    if settings.DEBUG and not settings.TEST_MODE:
        CACHED_PAGES = {}  # noqa

    if len(RESOURCE_HASHES.keys()) == 0:
        for r in list(Resource.objects.all()):
            RESOURCE_HASHES[r.name] = r.hashed_filename
            ALL_RESOURCES.append(r.hashed_filename)

    if page_slug in CACHED_PAGES:
        content = CACHED_PAGES[page_slug]
    else:
        try:
            page = Page.objects.get(slug__iexact=page_slug)
            content = page.rendered
        except Page.DoesNotExist:
            try:
                post = Post.objects.get(slug__iexact=page_slug)
                content = post.rendered
            except Post.DoesNotExist:
                if not settings.DEBUG:
                    raise Http404("Page does not exist")
                raise
        CACHED_PAGES[page_slug] = content

    content = multiple_replace(content, RESOURCE_HASHES)

    response = HttpResponse(content)
    response['Content-Length'] = len(content)
    return response


def resource(request, resource_slug):
    global RESOURCE_HASHES
    global CACHED_RESOURCES
    if len(RESOURCE_HASHES.keys()) == 0:
        for r in list(Resource.objects.all()):
            RESOURCE_HASHES[r.name] = r.hashed_filename
            ALL_RESOURCES.append(r.hashed_filename)

    if request.META.get('If-None-Match', ''):
        if request.META.get('If-None-Match') in ALL_RESOURCES:
            return HttpResponseNotModified()

    found_hashed = False
    if settings.DEBUG and not settings.TEST_MODE:
        CACHED_RESOURCES = {}  # noqa

    if resource_slug in CACHED_RESOURCES:
        return CACHED_RESOURCES[resource_slug]
    else:
        try:
            resource = Resource.objects.get(hashed_filename__iexact=resource_slug)
            content = resource.content
            found_hashed = True
        except:
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
    response['Content-Length'] = resource.content_size

    if found_hashed:
        response['Cache-Control'] = 'max-age=31536000'
        response['Expires'] = 'Thu, 09 Apr 2099 15:15:00 GMT'
        response['Etag'] = resource_slug

    CACHED_RESOURCES[resource_slug] = response
    return response
