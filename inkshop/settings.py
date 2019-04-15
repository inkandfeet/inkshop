import os
from sys import path

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
PROJECT_DIR = os.path.join(BASE_DIR, "inkshop")
APPS_DIR = os.path.join(PROJECT_DIR, "apps")
path.insert(0, BASE_DIR)
path.insert(0, PROJECT_DIR)
path.insert(0, APPS_DIR)


if 'ENV' in os.environ and os.environ["ENV"] == "live":
    from envs.live import *
else:
    from envs.dev import *
