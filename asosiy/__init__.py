"""
Asosiy - C2 Platform Package
"""

# Celery app import
from .celery import app as celery_app

__all__ = ('celery_app',)
