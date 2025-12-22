"""
ASGI config for Django C2 Platform
Supports both HTTP and WebSocket (Channels)
Production-ready for 10,000+ concurrent connections
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asosiy.settings')

# Initialize Django ASGI application early
django_asgi_app = get_asgi_application()

# Import routing after Django setup
from c2_core.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    # HTTP requests → Django
    'http': django_asgi_app,
    
    # WebSocket requests → Channels
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
