"""
Asosiy - C2 Platform URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from c2_agents.web_views import home_view, login_view, logout_view, agents_view, agent_detail_view

urlpatterns = [
    # Web Interface
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('agents/', agents_view, name='agents'),
    path('agents/<str:agent_id>/', agent_detail_view, name='agent_detail'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # Agent APIs (JSON)
    path('api/agent/', include('c2_agents.agent_urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
