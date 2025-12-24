"""
Asosiy - C2 Platform URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

def home(request):
    """API home page"""
    return JsonResponse({
        'status': 'online',
        'platform': 'C2 Platform',
        'version': '1.0.0',
        'message': 'Django server ishlayapti!',
        'endpoints': {
            'admin': '/admin/',
            'auth': {
                'login': '/api/auth/token/',
                'refresh': '/api/auth/token/refresh/',
            }
        }
    })

urlpatterns = [
    # Home
    path('', home, name='home'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentication (JWT Token)
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Agent APIs
    path('api/agent/', include('c2_agents.agent_urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
