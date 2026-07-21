import os
from celery import Celery
from decouple import config

# Uses Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', value=config('DJANGO_SETTINGS_MODULE'))

app = Celery('config')

# Reads config from Django settings with CELERY_prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discovers tasks in all installed apps
app.autodiscover_tasks()
