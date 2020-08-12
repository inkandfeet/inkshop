web: bin/start-stunnel uvicorn inkshop.asgi:application --host 0.0.0.0 --port $PORT  --workers=8
beat: bin/start-stunnel celery beat --app inkshop
celery: bin/start-stunnel celery worker --beat -c 8 -Q celery --app inkshop
