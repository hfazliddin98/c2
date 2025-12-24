"""
Agent API Endpoints
Barcha platform agentlari uchun umumiy endpoint'lar
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import time
from datetime import datetime

# In-memory agent storage (production'da Redis/Database ishlatish kerak)
AGENTS = {}
AGENT_COMMANDS = {}


@csrf_exempt
@require_http_methods(["POST"])
def register_agent(request):
    """
    Agent registration
    POST /api/agent/register
    
    Payload:
    {
        "type": "register",
        "device_info": {
            "device_id": "...",
            "platform": "Windows/Linux/Android",
            "hostname": "...",
            "username": "...",
            ...
        }
    }
    """
    try:
        data = json.loads(request.body)
        device_info = data.get('device_info', {})
        device_id = device_info.get('device_id')
        
        if not device_id:
            return JsonResponse({
                'status': 'error',
                'message': 'device_id required'
            }, status=400)
        
        # Save agent info
        AGENTS[device_id] = {
            'device_id': device_id,
            'platform': device_info.get('platform', 'Unknown'),
            'hostname': device_info.get('hostname', 'Unknown'),
            'username': device_info.get('username', 'Unknown'),
            'ip': request.META.get('REMOTE_ADDR'),
            'registered_at': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat(),
            'device_info': device_info,
            'status': 'online'
        }
        
        # Initialize command queue
        if device_id not in AGENT_COMMANDS:
            AGENT_COMMANDS[device_id] = []
        
        print(f"✅ Agent registered: {device_id} ({device_info.get('platform')})")
        
        return JsonResponse({
            'status': 'success',
            'message': 'Agent registered successfully',
            'agent_id': device_id
        })
        
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def heartbeat(request):
    """
    Agent heartbeat
    POST /api/agent/heartbeat
    
    Payload:
    {
        "device_id": "...",
        "timestamp": 1234567890
    }
    
    Response:
    {
        "status": "success",
        "commands": [
            {"type": "GET_LOCATION"},
            {"type": "VIBRATE"}
        ]
    }
    """
    try:
        data = json.loads(request.body)
        device_id = data.get('device_id')
        
        if not device_id:
            return JsonResponse({
                'status': 'error',
                'message': 'device_id required'
            }, status=400)
        
        # Update last seen
        if device_id in AGENTS:
            AGENTS[device_id]['last_seen'] = datetime.now().isoformat()
            AGENTS[device_id]['status'] = 'online'
        else:
            # Auto-register if not exists
            AGENTS[device_id] = {
                'device_id': device_id,
                'platform': 'Unknown',
                'ip': request.META.get('REMOTE_ADDR'),
                'registered_at': datetime.now().isoformat(),
                'last_seen': datetime.now().isoformat(),
                'status': 'online'
            }
            AGENT_COMMANDS[device_id] = []
        
        # Get pending commands
        commands = AGENT_COMMANDS.get(device_id, [])
        
        # Clear commands after sending
        AGENT_COMMANDS[device_id] = []
        
        return JsonResponse({
            'status': 'success',
            'commands': commands
        })
        
    except Exception as e:
        print(f"❌ Heartbeat error: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def list_agents(request):
    """
    List all agents
    GET /api/agent/list
    """
    try:
        # Filter offline agents (last_seen > 60 seconds ago)
        current_time = datetime.now()
        
        agents_list = []
        for agent_id, agent_data in AGENTS.items():
            last_seen = datetime.fromisoformat(agent_data['last_seen'])
            elapsed = (current_time - last_seen).total_seconds()
            
            if elapsed > 60:
                agent_data['status'] = 'offline'
            
            agents_list.append(agent_data)
        
        return JsonResponse({
            'status': 'success',
            'count': len(agents_list),
            'agents': agents_list
        })
        
    except Exception as e:
        print(f"❌ List agents error: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def send_command(request):
    """
    Send command to agent
    POST /api/agent/command
    
    Payload:
    {
        "device_id": "...",
        "command": {
            "type": "GET_LOCATION",
            "params": {}
        }
    }
    """
    try:
        data = json.loads(request.body)
        device_id = data.get('device_id')
        command = data.get('command')
        
        if not device_id or not command:
            return JsonResponse({
                'status': 'error',
                'message': 'device_id and command required'
            }, status=400)
        
        if device_id not in AGENTS:
            return JsonResponse({
                'status': 'error',
                'message': 'Agent not found'
            }, status=404)
        
        # Add command to queue
        if device_id not in AGENT_COMMANDS:
            AGENT_COMMANDS[device_id] = []
        
        AGENT_COMMANDS[device_id].append(command)
        
        print(f"✅ Command queued for {device_id}: {command.get('type')}")
        
        return JsonResponse({
            'status': 'success',
            'message': 'Command queued successfully'
        })
        
    except Exception as e:
        print(f"❌ Send command error: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def agent_result(request):
    """
    Agent command result
    POST /api/agent/result
    
    Payload:
    {
        "device_id": "...",
        "command_type": "GET_LOCATION",
        "result": {
            "latitude": 41.311158,
            "longitude": 69.279737
        }
    }
    """
    try:
        data = json.loads(request.body)
        device_id = data.get('device_id')
        command_type = data.get('command_type')
        result = data.get('result')
        
        print(f"📊 Result from {device_id}: {command_type}")
        print(f"   {result}")
        
        # Store result (production'da database'ga saqlash)
        if device_id in AGENTS:
            if 'results' not in AGENTS[device_id]:
                AGENTS[device_id]['results'] = []
            
            AGENTS[device_id]['results'].append({
                'command_type': command_type,
                'result': result,
                'timestamp': datetime.now().isoformat()
            })
        
        return JsonResponse({
            'status': 'success',
            'message': 'Result received'
        })
        
    except Exception as e:
        print(f"❌ Result error: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


def agent_status(request):
    """
    Server status
    GET /api/agent/status
    """
    return JsonResponse({
        'status': 'online',
        'total_agents': len(AGENTS),
        'online_agents': len([a for a in AGENTS.values() if a['status'] == 'online']),
        'server_time': datetime.now().isoformat()
    })
