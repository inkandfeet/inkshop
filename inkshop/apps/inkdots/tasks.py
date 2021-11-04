from celery.task import task
from inkdots.models import Event


@task
def log_request(**kwargs):
    Event.objects.create(**kwargs)
