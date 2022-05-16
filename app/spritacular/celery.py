import os

from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spritacular.settings')

app = Celery('spritacular')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
        # Scheduler Name
        'delete_blog_images': {
            'task': 'delete_unpublished_images',
            'schedule': crontab(minute="*/5"),  # 5 minutes
        },
}

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
