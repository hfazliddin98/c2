"""
Umumiy utility funksiyalar
"""

import json
import time
import platform
import socket
import psutil
import os
import sys
from datetime import datetime
from typing import Dict, Any


def is_windows() -> bool:
    """Windows platformini tekshirish"""
    return platform.system().lower() == 'windows'


def is_linux() -> bool:
    """Linux platformini tekshirish"""
    return platform.system().lower() == 'linux'


def is_macos() -> bool:
    """macOS platformini tekshirish"""
    return platform.system().lower() == 'darwin'


def get_platform_name() -> str:
    """Platform nomini olish"""
    system = platform.system().lower()
    if system == 'windows':
        return 'Windows'
    elif system == 'linux':
        return 'Linux'
    elif system == 'darwin':
        return 'macOS'
    else:
        return system.capitalize()


def get_shell_command(command_type: str) -> str:
    """Platformaga mos shell komanda olish"""
    commands = {
        'list_dir': 'dir' if is_windows() else 'ls -la',
        'clear': 'cls' if is_windows() else 'clear',
        'path_sep': '\\' if is_windows() else '/',
        'shell': 'cmd.exe' if is_windows() else '/bin/bash',
    }
    return commands.get(command_type, '')


def get_system_info() -> Dict[str, Any]:
    """Tizim ma'lumotlarini to'plash"""
    try:
        info = {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "platform_name": get_platform_name(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "processor": platform.processor(),
            "architecture": platform.architecture()[0],
            "username": os.getenv("USERNAME") or os.getenv("USER"),
            "ip_address": get_local_ip(),
            "python_version": sys.version,
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent
            },
            "cpu_percent": psutil.cpu_percent(),
            "cpu_count": psutil.cpu_count(),
            "boot_time": psutil.boot_time(),
            "timestamp": datetime.now().isoformat()
        }
        return info
    except Exception as e:
        return {"error": str(e)}


def get_local_ip() -> str:
    """Lokal IP manzilni olish"""
    try:
        # Google DNS serveriga ulanib IP ni aniqlash
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def format_bytes(bytes_value: int) -> str:
    """Baytlarni human-readable formatga o'girish"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def create_response(status: int, data: Any = None, message: str = "") -> Dict[str, Any]:
    """Standart response formati yaratish"""
    return {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "data": data,
        "message": message
    }


def validate_json(json_string: str) -> bool:
    """JSON formatini tekshirish"""
    try:
        json.loads(json_string)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def log_message(message: str, level: str = "INFO") -> None:
    """Log xabarini chiqarish"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


class CommandResult:
    """Komanda natijasini saqlash uchun klass"""
    
    def __init__(self, success: bool, output: str = "", error: str = ""):
        self.success = success
        self.output = output
        self.error = error
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "timestamp": self.timestamp
        }