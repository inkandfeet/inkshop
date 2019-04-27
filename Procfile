web: bin/start-stunnel gunicorn inkshop.wsgi -b "0.0.0.0:$PORT" --workers=8
beat: bin/start-stunnel celery beat --app inkshop
celery: bin/start-stunnel celery worker --beat -c 8 -Q celery --app inkshop
