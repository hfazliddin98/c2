# 🌐 Dynamic IP Configuration Guide

## Muammo

Agar serveringiz IP manzili o'zgarsa (home internet, cloud provider restart), agentlar bilan aloqa uziladi.

## ✅ Yechimlar

### 1️⃣ Dynamic DNS (DDNS) - ENG YAXSHI YECHIM

DDNS IP o'zgarsa ham domain name orqali serverga ulanishni ta'minlaydi.

#### Tavsiya Etiladigan DDNS Providerlar:

| Provider | Narx | Domain Soni | Qulayligi |
|----------|------|-------------|-----------|
| **DuckDNS** | ✅ Bepul | Cheksiz | ⭐⭐⭐⭐⭐ |
| **No-IP** | ✅ Bepul (3 ta) | 3 | ⭐⭐⭐⭐ |
| **Dynu** | ✅ Bepul (4 ta) | 4 | ⭐⭐⭐⭐ |
| **Cloudflare** | ✅ Bepul | Cheksiz | ⭐⭐⭐⭐⭐ |
| **FreeMyIP** | ✅ Bepul | Cheksiz | ⭐⭐⭐ |

---

### 📌 DuckDNS Setup (5 daqiqa)

**1. Account yaratish:**
- https://www.duckdns.org ga kiring
- GitHub/Google orqali login
- Token oling

**2. Subdomain yaratish:**
- `yourname.duckdns.org` domain tanlang
- Current IP ni avtomatik detect qiladi

**3. Auto-update qilish:**

**Linux/Mac (cron):**
```bash
# /etc/cron.d/duckdns
*/5 * * * * root echo url="https://www.duckdns.org/update?domains=yourname&token=YOUR_TOKEN&ip=" | curl -k -o /var/log/duckdns.log -K -
```

**Windows (Task Scheduler):**
```batch
@echo off
echo url="https://www.duckdns.org/update?domains=yourname&token=YOUR_TOKEN&ip=" | curl -k -o %TEMP%\duckdns.log -K -
```

**Python script:**
```python
import urllib.request

def update_duckdns(domain, token):
    url = f"https://www.duckdns.org/update?domains={domain}&token={token}&ip="
    urllib.request.urlopen(url)
    
# Her 5 daqiqada chaqiring
update_duckdns('yourname', 'YOUR_TOKEN')
```

**4. Agent'da ishlatish:**
```python
client = SmartClient()
client.add_server('yourname.duckdns.org', 9999)  # IP emas, domain!
```

---

### 2️⃣ IP Update Server (GitHub Gist / Pastebin)

Agar DDNS ishlatmasangiz, IP ni online file'da saqlang.

#### GitHub Gist Usuli:

**1. GitHub Gist yaratish:**
- https://gist.github.com ga kiring
- Yangi gist yarating: `server_config.json`

```json
{
  "server_ip": "123.45.67.89",
  "backup_ips": [
    "98.76.54.32",
    "11.22.33.44"
  ],
  "updated_at": "2025-12-23 10:00:00"
}
```

**2. Raw URL olish:**
```
https://gist.githubusercontent.com/username/gist_id/raw/server_config.json
```

**3. Agent'da ishlatish:**
```python
client = SmartClient()

# Fallback servers
client.add_server('old-server.com', 9999)

# GitHub Gist URL
client.add_ip_update_source('github_gist',
    'https://gist.githubusercontent.com/user/id/raw/server_config.json')

# Har 5 daqiqada yangi IP tekshiriladi
client.run()
```

**4. IP o'zgarganda:**
- Gist ni yangilang (yangi IP qo'shing)
- Agent avtomatik 5 daqiqada yangi IP ni topadi

---

#### Pastebin Usuli:

**1. Pastebin paste yarating:**
- https://pastebin.com ga kiring
- Yangi paste:

```
123.45.67.89
98.76.54.32
11.22.33.44
```

**2. Raw URL olish:**
```
https://pastebin.com/raw/xxxxx
```

**3. Agent'da ishlatish:**
```python
client.add_ip_update_source('pastebin',
    'https://pastebin.com/raw/xxxxx')
```

---

### 3️⃣ Multiple Fallback Servers

Bir nechta server IP larini agent'ga qo'shing:

```python
client = SmartClient()

# Primary
client.add_server('primary.example.com', 9999)

# Backups
client.add_server('backup1.example.com', 9999)
client.add_server('backup2.example.com', 9999)
client.add_server('123.45.67.89', 9999)  # IP backup

# Agar biri ishlamasa, keyingisiga o'tadi
client.run()
```

---

### 4️⃣ Cloudflare DDNS (Professional)

**Afzalliklari:**
- ✅ Bepul SSL/TLS
- ✅ DDoS protection
- ✅ CDN
- ✅ Professional

**Setup:**

**1. Domain sotib oling (yoki bepul subdomain):**
- Namecheap, GoDaddy, etc.

**2. Cloudflare ga qo'shing:**
- https://dash.cloudflare.com
- Add site
- Nameserver o'zgartiring

**3. API token oling:**
- My Profile → API Tokens
- Create Token → Edit zone DNS

**4. Auto-update script:**
```python
import requests

def update_cloudflare(zone_id, record_id, api_token, new_ip):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "type": "A",
        "name": "c2.yourdomain.com",
        "content": new_ip,
        "ttl": 120,
        "proxied": False
    }
    
    response = requests.put(url, json=data, headers=headers)
    return response.json()

# IP o'zgarganda chaqiring
update_cloudflare('YOUR_ZONE_ID', 'YOUR_RECORD_ID', 'YOUR_TOKEN', '1.2.3.4')
```

---

## 🎯 Recommended Setup

**Best Practice (Eng xavfsiz):**

1. **Cloudflare DDNS:**
   - Domain: `c2.yourdomain.com`
   - Auto-update script (har 5 daqiqada)
   
2. **GitHub Gist backup:**
   - Private gist
   - Backup IP list
   
3. **Agent configuration:**
```python
client = SmartClient()

# Primary: Cloudflare DDNS domain
client.add_server('c2.yourdomain.com', 9999)

# Backup: Direct IP
client.add_server('123.45.67.89', 9999)

# IP update: GitHub Gist
client.add_ip_update_source('github_gist',
    'https://gist.githubusercontent.com/user/id/raw/config.json')

client.run()
```

---

## 🔧 Qo'shimcha Tools

### IP o'zgarganini tekshirish:

```python
import urllib.request

def get_public_ip():
    """Hozirgi public IP ni olish"""
    try:
        response = urllib.request.urlopen('https://api.ipify.org')
        return response.read().decode()
    except:
        # Alternative
        response = urllib.request.urlopen('https://ifconfig.me')
        return response.read().decode()

print(f"Sizning IP: {get_public_ip()}")
```

### Auto IP updater (server-side):

```python
import time
import json

def monitor_and_update_ip(gist_url, gist_token, check_interval=300):
    """IP o'zgarsa avtomatik gist ni yangilash"""
    
    last_ip = None
    
    while True:
        current_ip = get_public_ip()
        
        if current_ip != last_ip:
            print(f"🔄 IP o'zgardi: {last_ip} → {current_ip}")
            
            # Gist ni yangilash
            update_gist(gist_url, gist_token, current_ip)
            
            last_ip = current_ip
            
        time.sleep(check_interval)
```

---

## 📊 Comparison

| Usul | Narx | Qulayligi | Tezligi | Xavfsizligi |
|------|------|-----------|---------|-------------|
| **DuckDNS** | Bepul | ⭐⭐⭐⭐⭐ | Fast | Medium |
| **Cloudflare** | Bepul | ⭐⭐⭐⭐ | Very Fast | High |
| **GitHub Gist** | Bepul | ⭐⭐⭐ | Medium | Medium |
| **Pastebin** | Bepul | ⭐⭐⭐⭐ | Medium | Low |
| **Multiple IPs** | Bepul | ⭐⭐ | Fast | Medium |

---

## 💡 Tips

1. **Har doim backup qo'shing** - Primary ishlamasa
2. **Update interval = 5 daqiqa** - Tez-tez check qilmang
3. **Private gist ishlatng** - Public gist xavfli
4. **SSL/TLS ishlatng** - HTTPS, WSS
5. **Domain name eng yaxshi** - Professional ko'rinish

---

✅ **Tayyor!** Endi IP o'zgarsa ham agent ulanadi! 🚀
