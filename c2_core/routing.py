"""
C2 Core App - WebSocket Routing
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Agent WebSocket
    re_path(r'ws/agent/(?P<agent_id>[0-9a-f-]+)/$', consumers.AgentConsumer.as_asgi()),
    
    # Operator Dashboard WebSocket
    re_path(r'ws/operator/$', consumers.OperatorConsumer.as_asgi()),
]
