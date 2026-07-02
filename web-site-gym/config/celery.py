import os
from celery import Celery

# Uses Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('config')

# Reads config from Django settings with CELERY_prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discovers tasks in all installed apps
app.autodiscover_tasks()
