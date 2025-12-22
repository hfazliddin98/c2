"""
IP Updater - Agar server IP o'zgarsa, agentlar yangi IP ni topish uchun
"""
import json
import urllib.request
import urllib.error
import time


class IPUpdater:
    """Server IP'ni dinamik yangilash"""
    
    def __init__(self):
        self.update_sources = []
        
    def add_github_gist(self, gist_url):
        """GitHub Gist orqali IP update
        
        Example:
            https://gist.githubusercontent.com/username/gist_id/raw/config.json
            
            config.json:
            {
                "server_ip": "1.2.3.4",
                "backup_ips": ["5.6.7.8", "9.10.11.12"],
                "updated_at": "2025-12-23 10:00:00"
            }
        """
        self.update_sources.append({
            'type': 'github_gist',
            'url': gist_url
        })
        
    def add_pastebin(self, pastebin_raw_url):
        """Pastebin orqali IP update
        
        Example:
            https://pastebin.com/raw/xxxxx
            
            Content:
            1.2.3.4
            5.6.7.8
            9.10.11.12
        """
        self.update_sources.append({
            'type': 'pastebin',
            'url': pastebin_raw_url
        })
        
    def add_custom_url(self, url):
        """Custom URL orqali IP update
        
        JSON yoki text format qabul qiladi
        """
        self.update_sources.append({
            'type': 'custom',
            'url': url
        })
        
    def get_updated_ips(self, timeout=5):
        """Barcha manbalardan yangi IP larni olish
        
        Returns:
            list: [primary_ip, backup_ip1, backup_ip2, ...]
        """
        all_ips = []
        
        for source in self.update_sources:
            try:
                ips = self._fetch_from_source(source, timeout)
                all_ips.extend(ips)
            except Exception as e:
                print(f"❌ {source['type']} dan olib bo'lmadi: {e}")
                continue
                
        # Dublikatlarni olib tashlash
        unique_ips = []
        for ip in all_ips:
            if ip not in unique_ips:
                unique_ips.append(ip)
                
        return unique_ips
        
    def _fetch_from_source(self, source, timeout):
        """Bir manbadan IP larni olish"""
        url = source['url']
        
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            with urllib.request.urlopen(req, timeout=timeout) as response:
                content = response.read().decode('utf-8')
                
            if source['type'] == 'github_gist':
                return self._parse_json(content)
            elif source['type'] == 'pastebin':
                return self._parse_text(content)
            elif source['type'] == 'custom':
                # Try JSON first, then text
                try:
                    return self._parse_json(content)
                except:
                    return self._parse_text(content)
                    
        except urllib.error.URLError as e:
            raise Exception(f"URL xatosi: {e}")
        except Exception as e:
            raise Exception(f"Fetch xatosi: {e}")
            
        return []
        
    def _parse_json(self, content):
        """JSON formatni parse qilish"""
        data = json.loads(content)
        
        ips = []
        
        # server_ip field
        if 'server_ip' in data:
            ips.append(data['server_ip'])
            
        # backup_ips field
        if 'backup_ips' in data:
            ips.extend(data['backup_ips'])
            
        # ips array
        if 'ips' in data:
            ips.extend(data['ips'])
            
        return ips
        
    def _parse_text(self, content):
        """Text formatni parse qilish"""
        lines = content.strip().split('\n')
        ips = []
        
        for line in lines:
            line = line.strip()
            # IP format check (oddiy)
            if line and '.' in line:
                parts = line.split('.')
                if len(parts) == 4:
                    try:
                        # Har bir qism 0-255 orasida
                        valid = all(0 <= int(p) <= 255 for p in parts)
                        if valid:
                            ips.append(line)
                    except:
                        pass
                        
        return ips


class DynamicDNS:
    """Dynamic DNS (DDNS) providers"""
    
    PROVIDERS = {
        'no-ip': {
            'name': 'No-IP',
            'url': 'https://www.noip.com',
            'free': True,
            'description': 'Eng mashhur DDNS, 3 ta domain bepul'
        },
        'duckdns': {
            'name': 'DuckDNS',
            'url': 'https://www.duckdns.org',
            'free': True,
            'description': 'To\'liq bepul, cheksiz subdomain'
        },
        'dynu': {
            'name': 'Dynu',
            'url': 'https://www.dynu.com',
            'free': True,
            'description': '4 ta domain bepul'
        },
        'freemyip': {
            'name': 'FreeMyIP',
            'url': 'https://freemyip.com',
            'free': True,
            'description': 'Oddiy, tez'
        },
        'cloudflare': {
            'name': 'Cloudflare',
            'url': 'https://www.cloudflare.com',
            'free': True,
            'description': 'Professional, SSL bepul'
        }
    }
    
    @classmethod
    def get_providers(cls):
        """Barcha DDNS providerlarni olish"""
        return cls.PROVIDERS
        
    @classmethod
    def get_recommendations(cls):
        """Tavsiya etiladigan providerlar"""
        return ['duckdns', 'no-ip', 'cloudflare']


def create_ip_config(primary_ip, backup_ips=None, gist_url=None):
    """IP config yaratish
    
    Bu config ni GitHub Gist yoki Pastebin ga yuklash mumkin
    """
    config = {
        'server_ip': primary_ip,
        'backup_ips': backup_ips or [],
        'updated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'gist_url': gist_url
    }
    
    return json.dumps(config, indent=2)


if __name__ == '__main__':
    # Test
    print("🔧 IP Updater Test\n")
    
    # Example: GitHub Gist
    print("📝 GitHub Gist config example:")
    config = create_ip_config(
        primary_ip='123.45.67.89',
        backup_ips=['98.76.54.32', '11.22.33.44']
    )
    print(config)
    print()
    
    # DDNS providers
    print("🌐 DDNS Providers:")
    for key, provider in DynamicDNS.PROVIDERS.items():
        free = "✅ BEPUL" if provider['free'] else "💰 PULLIK"
        print(f"  {provider['name']}: {provider['description']} - {free}")
    print()
    
    # IP updater test
    updater = IPUpdater()
    
    # Example: O'zingizning gist URL
    # updater.add_github_gist('https://gist.githubusercontent.com/user/id/raw/config.json')
    
    print("✅ IPUpdater tayyor!")
    print("📌 Gist URL qo'shing: updater.add_github_gist('your_url')")
