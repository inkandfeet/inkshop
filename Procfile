web: bin/start-stunnel && gunicorn inkshop.wsgi -b "0.0.0.0:$PORT" --workers=10
beat: bin/start-stunnel && DJANGO_SETTINGS_MODULE=inkshop.envs.live celery beat --app inkshop
celery: bin/start-stunnel && DJANGO_SETTINGS_MODULE=inkshop.envs.live celery worker -c 12 -Q celery --app inkshop
