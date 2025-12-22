"""
Asosiy - C2 Platform URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

def home(request):
    """API home page"""
    return JsonResponse({
        'status': 'online',
        'platform': 'C2 Platform',
        'version': '1.0.0',
        'message': 'Django server ishlayapti!',
        'endpoints': {
            'admin': '/admin/',
        }
    })

urlpatterns = [
    # Home
    path('', home, name='home'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentication - muvaqqatan o'chirilgan
    # path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # C2 APIs - muvaqqatan o'chirilgan
    # path('api/agents/', include('c2_agents.urls')),
    # path('api/listeners/', include('c2_listeners.urls')),
    # path('api/commands/', include('c2_commands.urls')),
    # path('api/core/', include('c2_core.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
