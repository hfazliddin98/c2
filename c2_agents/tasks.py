"""
C2 Agents App - Celery Tasks
Async task processing for scalability
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task(bind=True, max_retries=3)
def process_heartbeat_async(self, agent_id, ip_address=None):
    """
    Process agent heartbeat asynchronously
    Optimized for 10,000+ concurrent heartbeats
    """
    from .models import Agent
    
    try:
        agent = Agent.objects.get(id=agent_id)
        agent.last_seen = timezone.now()
        agent.status = 'active'
        
        if ip_address:
            agent.ip_address = ip_address
        
        # Bulk update (more efficient)
        Agent.objects.filter(id=agent_id).update(
            last_seen=timezone.now(),
            status='active'
        )
        
        return {'status': 'success', 'agent_id': str(agent_id)}
        
    except Agent.DoesNotExist:
        return {'status': 'error', 'message': 'Agent not found'}
    except Exception as e:
        # Retry on failure
        raise self.retry(exc=e, countdown=5)


@shared_task
def cleanup_offline_agents():
    """
    Mark agents as offline if no heartbeat > 5 minutes
    Runs periodically (cron-like)
    """
    from .models import Agent
    
    timeout = timezone.now() - timedelta(minutes=5)
    
    updated = Agent.objects.filter(
        status='active',
        last_seen__lt=timeout
    ).update(status='offline')
    
    return {'updated': updated}


@shared_task
def delete_old_agents():
    """
    Delete agents offline for > 7 days
    """
    from .models import Agent
    
    threshold = timezone.now() - timedelta(days=7)
    
    deleted, _ = Agent.objects.filter(
        status='offline',
        last_seen__lt=threshold
    ).delete()
    
    return {'deleted': deleted}


@shared_task(bind=True)
def bulk_agent_command(self, agent_ids, command_type, command_data):
    """
    Send command to multiple agents (bulk operation)
    """
    from c2_commands.models import Command
    
    commands = []
    for agent_id in agent_ids:
        commands.append(Command(
            agent_id=agent_id,
            command_type=command_type,
            command_data=command_data,
            status='pending'
        ))
    
    # Bulk create (efficient)
    Command.objects.bulk_create(commands, batch_size=1000)
    
    return {'created': len(commands)}
