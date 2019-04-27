from django_hosts.resolvers import reverse as hosts_reverse


def reverse(*args, **kwargs):
    # kwargs["host"] = "clubhouse"
    if "host" in kwargs:
        return "/%s" % hosts_reverse(*args, **kwargs).replace("://", "")
    return hosts_reverse(*args, **kwargs).replace("://", "")
