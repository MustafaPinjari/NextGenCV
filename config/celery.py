"""
Celery application configuration for NextGenCV.

Handles async task processing for:
- PDF parsing (10-30s blocking → background)
- Resume optimization (AI calls → background)
- ATS analysis (scoring → background)
- Email sending
"""
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('nextgencv')

# Load config from Django settings, using CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
