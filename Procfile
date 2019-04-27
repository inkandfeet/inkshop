web: bin/start-stunnel && LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 gunicorn inkshop.wsgi -b "0.0.0.0:$PORT" --workers=8
# beat: bin/start-stunnel && DJANGO_SETTINGS_MODULE=inkshop.envs.live LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 celery beat --app inkshop
celery: bin/start-stunnel && DJANGO_SETTINGS_MODULE=inkshop.envs.live LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 celery worker --beat -c 12 -Q celery --app inkshop
