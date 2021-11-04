from ipware import get_client_ip
from inkdots.tasks import log_request


EXCLUDE_PARTIALS = [
    "static/",
]


class InkDotsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            exclude = False
            for exc in EXCLUDE_PARTIALS:
                if exc in request.path:
                    exclude = True
                    break
            if not exclude:
                log_request.delay(
                    event_type="page_view",
                    base_url=request.path,
                    querystring=request.get_full_path().split("?")[1],
                    full_url=request.build_absolute_uri(request.get_full_path()),
                    data={},
                    request_ip=get_client_ip(request)[0],
                    request_ua=request.META.get("HTTP_USER_AGENT", "None")
                )
        except:
            pass

        response = self.get_response(request)

        return response
