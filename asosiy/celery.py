"""
Celery configuration for Django C2 Platform
Async task processing for 10,000+ users
"""

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asosiy.settings')

app = Celery('asosiy')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task"""
    print(f'Request: {self.request!r}')
