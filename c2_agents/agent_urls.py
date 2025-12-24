"""
Agent API URLs
"""

from django.urls import path
from . import agent_api

urlpatterns = [
    # Agent endpoints
    path('register', agent_api.register_agent, name='agent_register'),
    path('heartbeat', agent_api.heartbeat, name='agent_heartbeat'),
    path('list', agent_api.list_agents, name='agent_list'),
    path('command', agent_api.send_command, name='agent_command'),
    path('result', agent_api.agent_result, name='agent_result'),
    path('status', agent_api.agent_status, name='agent_status'),
]
