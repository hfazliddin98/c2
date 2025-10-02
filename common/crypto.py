"""
Shifrash va xavfsizlik funksiyalari
"""

import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import json


class CryptoManager:
    """Shifrash va deshifrash uchun klass"""
    
    def __init__(self, password: str = None):
        if password:
            self.key = self._derive_key(password)
        else:
            self.key = Fernet.generate_key()
        self.fernet = Fernet(self.key)
    
    def _derive_key(self, password: str) -> bytes:
        """Paroldan key hosil qilish"""
        password_bytes = password.encode()
        salt = b'salt_for_c2_platform'  # Real loyihada random salt ishlatish kerak
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return key
    
    def encrypt(self, data: str) -> str:
        """Ma'lumotni shifrlash"""
        encrypted = self.fernet.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Ma'lumotni deshifrlash"""
        try:
            decoded = base64.b64decode(encrypted_data.encode())
            decrypted = self.fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Deshifrash xatosi: {e}")
    
    def get_key(self) -> str:
        """Key'ni string formatida qaytarish"""
        return base64.b64encode(self.key).decode()


def generate_agent_id() -> str:
    """Noyob agent ID yaratish"""
    import uuid
    return str(uuid.uuid4())


def hash_password(password: str) -> str:
    """Parolni hash qilish"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Parolni tekshirish"""
    return hash_password(password) == hashed