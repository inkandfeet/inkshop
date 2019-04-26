# -*- coding: utf-8 -*-
import os
from sys import path

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
APPS_DIR = os.path.join(BASE_DIR, "apps")
path.insert(0, BASE_DIR)
path.insert(0, APPS_DIR)


if 'ENV' in os.environ and os.environ["ENV"] == "live":
    from inkshop.envs.live import *
else:
    from inkshop.envs.dev import *
