# -*- coding: utf-8 -*-
from django.conf import settings
from django_hosts import patterns, host

host_patterns = patterns(
    '',
    host(r'', 'inkshop.host_urls.root', name='root'),
    host(r'dots', 'inkshop.host_urls.dots', name='dots'),
    host(r'clubhouse', 'inkshop.host_urls.clubhouse', name='clubhouse'),
    host(r'mail', 'inkshop.host_urls.mail', name='inkmail'),
)
