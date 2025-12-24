"""
JWT Login Manager - C2 Platform
Havoc GUI va CLI uchun JWT autentifikatsiya
"""

import requests
import json
import os
from pathlib import Path

class JWTAuthManager:
    """JWT token boshqaruvi"""
    
    def __init__(self, server_url, verify_ssl=False):
        """
        Args:
            server_url: Django server URL (masalan: https://localhost:8443)
            verify_ssl: SSL sertifikatni tekshirish (False = self-signed uchun)
        """
        self.server_url = server_url.rstrip('/')
        self.session = requests.Session()
        self.session.verify = verify_ssl  # Self-signed cert uchun False
        
        # Token saqlash fayli
        self.token_file = Path.home() / '.c2_tokens.json'
        self.access_token = None
        self.refresh_token = None
        
        # Mavjud tokenni yuklash
        self._load_tokens()
    
    def login(self, username, password):
        """
        Django API ga login qilish va JWT token olish
        
        Args:
            username: Django foydalanuvchi nomi
            password: Parol
            
        Returns:
            bool: Muvaffaqiyatli login True, aks holda False
        """
        try:
            url = f"{self.server_url}/api/auth/token/"
            data = {
                'username': username,
                'password': password
            }
            
            response = self.session.post(url, json=data)
            
            if response.status_code == 200:
                tokens = response.json()
                self.access_token = tokens.get('access')
                self.refresh_token = tokens.get('refresh')
                
                # Tokenlarni saqlash
                self._save_tokens()
                
                # Session headers ni yangilash
                self.session.headers['Authorization'] = f'Bearer {self.access_token}'
                
                print(f"[+] Login muvaffaqiyatli: {username}")
                return True
            else:
                print(f"[!] Login xatolik: {response.status_code}")
                print(f"    {response.text}")
                return False
                
        except requests.exceptions.SSLError:
            print("[!] SSL sertifikat xatolik!")
            print("    verify_ssl=False qo'ying yoki to'g'ri sertifikat ishlatilng")
            return False
        except Exception as e:
            print(f"[!] Login xatolik: {e}")
            return False
    
    def refresh(self):
        """
        Access token yangilash (refresh token bilan)
        
        Returns:
            bool: Muvaffaqiyatli refresh True, aks holda False
        """
        if not self.refresh_token:
            print("[!] Refresh token mavjud emas, qayta login qiling")
            return False
        
        try:
            url = f"{self.server_url}/api/auth/token/refresh/"
            data = {'refresh': self.refresh_token}
            
            response = self.session.post(url, json=data)
            
            if response.status_code == 200:
                tokens = response.json()
                self.access_token = tokens.get('access')
                
                # Yangi refresh token ham kelishi mumkin
                if 'refresh' in tokens:
                    self.refresh_token = tokens.get('refresh')
                
                # Tokenlarni saqlash
                self._save_tokens()
                
                # Session headers ni yangilash
                self.session.headers['Authorization'] = f'Bearer {self.access_token}'
                
                print("[+] Token yangilandi")
                return True
            else:
                print(f"[!] Refresh xatolik: {response.status_code}")
                print("    Qayta login qiling")
                self.access_token = None
                self.refresh_token = None
                return False
                
        except Exception as e:
            print(f"[!] Refresh xatolik: {e}")
            return False
    
    def logout(self):
        """Tokenlarni o'chirish"""
        self.access_token = None
        self.refresh_token = None
        
        if self.token_file.exists():
            self.token_file.unlink()
        
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
        
        print("[+] Logout muvaffaqiyatli")
    
    def is_authenticated(self):
        """
        Token mavjudligini tekshirish
        
        Returns:
            bool: Authenticated True, aks holda False
        """
        return self.access_token is not None
    
    def get_session(self):
        """
        Authenticated requests.Session obyektini olish
        
        Returns:
            requests.Session: JWT token bilan sozlangan session
        """
        return self.session
    
    def _save_tokens(self):
        """Tokenlarni faylga saqlash"""
        try:
            tokens = {
                'access': self.access_token,
                'refresh': self.refresh_token
            }
            
            with open(self.token_file, 'w') as f:
                json.dump(tokens, f)
            
            # Faylni faqat o'qish uchun (Windows)
            os.chmod(self.token_file, 0o600)
            
        except Exception as e:
            print(f"[!] Token saqlash xatolik: {e}")
    
    def _load_tokens(self):
        """Fayldan tokenlarni yuklash"""
        try:
            if self.token_file.exists():
                with open(self.token_file, 'r') as f:
                    tokens = json.load(f)
                
                self.access_token = tokens.get('access')
                self.refresh_token = tokens.get('refresh')
                
                if self.access_token:
                    self.session.headers['Authorization'] = f'Bearer {self.access_token}'
                    
        except Exception as e:
            print(f"[!] Token yuklash xatolik: {e}")


# Example usage
if __name__ == "__main__":
    # HTTPS server bilan
    auth = JWTAuthManager(
        server_url="https://localhost:8443",
        verify_ssl=False  # Self-signed cert uchun
    )
    
    # Login
    if auth.login("admin", "admin123"):
        print("[+] Authenticated!")
        
        # API so'rovlar
        session = auth.get_session()
        
        # Test request
        try:
            response = session.get("https://localhost:8443/api/")
            print(f"[+] API response: {response.status_code}")
            print(response.json())
        except Exception as e:
            print(f"[!] API xatolik: {e}")
        
        # Logout
        auth.logout()
    else:
        print("[!] Login xatolik!")
