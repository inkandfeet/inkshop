#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import locale
try:
    locale.setlocale(locale.LC_ALL, str('en_US.UTF-8'))
    locale.setlocale(locale.LANG, str('en_US.UTF-8'))
except:
    locale.setlocale(locale.LC_ALL, str('C.UTF-8'))
    # locale.setlocale(locale.LANG, str('C.UTF-8'))

import os
os.environ["LANG"] = 'en_US.UTF-8'
os.environ["LC_ALL"] = 'en_US.UTF-8'
import sys
from sys import path

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
PROJECT_DIR = os.path.join(BASE_DIR, "inkshop")
APPS_DIR = os.path.join(PROJECT_DIR, "apps")
path.insert(0, BASE_DIR)
path.insert(0, PROJECT_DIR)
path.insert(0, APPS_DIR)


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inkshop.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
