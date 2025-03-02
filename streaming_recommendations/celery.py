# streaming_recommendations/celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'streaming_recommendations.settings')

app = Celery('streaming_recommendations')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'update-content-cache': {
        'task': 'recommender.tasks.update_content_cache',
        'schedule': 3600.0,  # Run every hour
    },
    'update-recommendations': {
        'task': 'recommender.tasks.update_recommendations',
        'schedule': 86400.0,  # Run daily
    },
}