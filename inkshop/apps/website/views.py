from django.conf import settings
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404

from annoying.decorators import render_to, ajax_request
from website.models import Page, Post

CACHED_PAGES = {}


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
            except:
                raise Http404("Page does not exist")

    response = HttpResponse(content)
    response['Content-Length'] = len(content)
    return response
