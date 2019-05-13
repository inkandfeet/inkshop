# -*- coding: utf-8 -*-
from django.conf import settings
from django_hosts import patterns, host

if hasattr(settings, "IS_LIVE") and settings.IS_LIVE:
    host_patterns = patterns(
        '',
        host(r'', 'inkshop.host_urls.website', name='website'),
        host(r'dots', 'inkshop.host_urls.dots', name='dots'),
        host(r'clubhouse', 'inkshop.host_urls.clubhouse', name='clubhouse'),
        host(r'mail', 'inkshop.host_urls.mail', name='mail'),
        host(r'draft', 'inkshop.host_urls.website', name='draft'),
        host(r'root', 'inkshop.host_urls.website', name='root'),
    )
else:
    host_patterns = patterns(
        '',
        host(r'', 'inkshop.host_urls.root', name='root'),
        host(r'dots', 'inkshop.host_urls.dots', name='dots'),
        host(r'clubhouse', 'inkshop.host_urls.clubhouse', name='clubhouse'),
        host(r'mail', 'inkshop.host_urls.mail', name='mail'),
        host(r'draft', 'inkshop.host_urls.website', name='draft'),
        host(r'website', 'inkshop.host_urls.website', name='website'),
    )
