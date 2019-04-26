# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import locale
try:
    locale.setlocale(locale.LC_ALL, str('en_US.UTF-8'))
    locale.setlocale(locale.LANG, str('en_US.UTF-8'))
except:
    locale.setlocale(locale.LC_ALL, str('C.UTF-8'))
    # locale.setlocale(locale.LANG, str('C.UTF-8'))
os.environ["LANG"] = 'en_US.UTF-8'
os.environ["LC_ALL"] = 'en_US.UTF-8'

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery_tasks import app as celery_app

__all__ = ['celery_app']
