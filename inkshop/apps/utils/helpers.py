from django.urls import reverse as django_reverse


def reverse(*args, **kwargs):
    # from django_hosts.resolvers import reverse as hosts_reverse
    # kwargs["host"] = "clubhouse"
    # if "host" in kwargs:
    #     return "/%s" % hosts_reverse(*args, **kwargs).replace("://", "")
    # return hosts_reverse(*args, **kwargs).replace("://", "")
    if "host" in kwargs:
        del kwargs["host"]
    return django_reverse(*args, **kwargs)


def get_me(request):
    from people.models import Person
    if request.user and request.user.pk:
        return Person.objects.get(pk=request.user.pk)
    else:
        return None
