"""
Network IP Helper - Network IP manzillarini aniqlash
"""
import socket


def get_local_ip():
    """Local network IP manzilini aniqlash
    
    Returns:
        str: Local IP (masalan, 192.168.1.100)
    """
    try:
        # Method 1: Test connection orqali (eng ishonchli)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        # Google DNS ga "ulanish" (real connection yo'q, faqat routing)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        pass
    
    try:
        # Method 2: Hostname orqali
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        # 127.x.x.x ni skip qilish
        if not local_ip.startswith('127.'):
            return local_ip
    except:
        pass
    
    # Method 3: Barcha network interface'larni tekshirish (Windows/Linux)
    try:
        import netifaces
        for interface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    ip = addr['addr']
                    # 127.x.x.x va 169.x.x.x ni skip qilish
                    if not ip.startswith('127.') and not ip.startswith('169.'):
                        return ip
    except ImportError:
        pass
    
    # Fallback
    return '127.0.0.1'


def get_all_ips():
    """Barcha IP manzillarni olish
    
    Returns:
        dict: {'hostname': str, 'local_ip': str, 'all_ips': list}
    """
    info = {
        'hostname': socket.gethostname(),
        'local_ip': get_local_ip(),
        'all_ips': []
    }
    
    # Barcha IP larni qidirish
    try:
        import netifaces
        for interface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    ip = addr['addr']
                    if ip not in info['all_ips']:
                        info['all_ips'].append(ip)
    except ImportError:
        # netifaces yo'q bo'lsa, hostname orqali
        try:
            hostname_ip = socket.gethostbyname(info['hostname'])
            info['all_ips'].append(hostname_ip)
        except:
            pass
        
        # Local IP qo'shish
        if info['local_ip'] not in info['all_ips']:
            info['all_ips'].append(info['local_ip'])
    
    return info


def get_public_ip():
    """Public (internet) IP ni aniqlash
    
    Returns:
        str: Public IP yoki None
    """
    import urllib.request
    
    services = [
        'https://api.ipify.org',
        'https://ifconfig.me/ip',
        'https://icanhazip.com'
    ]
    
    for service in services:
        try:
            req = urllib.request.Request(service, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as response:
                return response.read().decode('utf-8').strip()
        except:
            continue
    
    return None


def show_network_info():
    """Network ma'lumotlarini ko'rsatish"""
    print("=" * 60)
    print("🌐 NETWORK INFORMATION")
    print("=" * 60)
    
    info = get_all_ips()
    
    print(f"\n💻 Hostname: {info['hostname']}")
    print(f"📍 Local IP: {info['local_ip']}")
    
    if len(info['all_ips']) > 1:
        print(f"\n📋 Barcha IP manzillar:")
        for i, ip in enumerate(info['all_ips'], 1):
            print(f"   {i}. {ip}")
    
    print(f"\n🌍 Public IP ni aniqlash...")
    public_ip = get_public_ip()
    if public_ip:
        print(f"   ✅ Public IP: {public_ip}")
    else:
        print(f"   ❌ Public IP aniqlanmadi (internet yo'q?)")
    
    print("\n" + "=" * 60)
    print("📱 ULANISH MA'LUMOTLARI")
    print("=" * 60)
    
    print(f"\n🔵 Local network dan ulanish (Wi-Fi/Ethernet):")
    print(f"   Server IP: {info['local_ip']}")
    print(f"   Misol: {info['local_ip']}:9999")
    
    print(f"\n🌐 Internet orqali ulanish:")
    if public_ip:
        print(f"   Server IP: {public_ip}")
        print(f"   Misol: {public_ip}:9999")
        print(f"   ⚠️  Port forwarding kerak!")
    else:
        print(f"   ❌ Public IP yo'q")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    show_network_info()
