"""
C2 Agents App - Models
"""

from django.db import models
from django.utils import timezone
import uuid


class Agent(models.Model):
    """Agent model - represents connected clients"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('idle', 'Idle'),
        ('offline', 'Offline'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_id = models.CharField(max_length=255, unique=True, db_index=True)  # Agent unique ID
    hostname = models.CharField(max_length=255)
    username = models.CharField(max_length=255, blank=True, default='')
    platform = models.CharField(max_length=100)
    architecture = models.CharField(max_length=50, default='x64')  # x64, x86, arm
    ip_address = models.GenericIPAddressField()
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-last_seen']
        indexes = [
            models.Index(fields=['status', '-last_seen']),
            models.Index(fields=['hostname']),
        ]
    
    def __str__(self):
        return f"{self.hostname} ({self.username})"
    
    def is_online(self):
        """Check if agent is online (heartbeat < 5 minutes)"""
        from datetime import timedelta
        timeout = timezone.now() - timedelta(minutes=5)
        return self.last_seen > timeout
