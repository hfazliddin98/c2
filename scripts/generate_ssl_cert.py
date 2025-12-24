"""
SSL Sertifikat Generator
C2 Platform uchun HTTPS sertifikat yaratadi
"""

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime
import os

def generate_ssl_certificate():
    """Self-signed SSL sertifikat yaratish"""
    
    # Certs papkasini yaratish
    certs_dir = os.path.join(os.path.dirname(__file__), '..', 'certs')
    os.makedirs(certs_dir, exist_ok=True)
    
    print("\n" + "="*50)
    print("   SSL SERTIFIKAT GENERATOR")
    print("="*50 + "\n")
    
    print("[*] Private key yaratilmoqda...")
    # Private key yaratish
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    print("[*] Sertifikat yaratilmoqda...")
    # Sertifikat ma'lumotlari
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "UZ"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Tashkent"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Tashkent"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "C2Platform"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Security"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])
    
    # Sertifikat yaratish
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.now(datetime.UTC)
    ).not_valid_after(
        datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=365)
    ).sign(private_key, hashes.SHA256())
    
    # Private key saqlash
    key_path = os.path.join(certs_dir, 'server.key')
    with open(key_path, 'wb') as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # Certificate saqlash
    cert_path = os.path.join(certs_dir, 'server.crt')
    with open(cert_path, 'wb') as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    # PEM format (certificate + key)
    pem_path = os.path.join(certs_dir, 'server.pem')
    with open(pem_path, 'wb') as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    print("\n[+] SSL sertifikat muvaffaqiyatli yaratildi!\n")
    print("Fayllar:")
    print(f"  - {key_path}  (Private Key)")
    print(f"  - {cert_path}  (Certificate)")
    print(f"  - {pem_path}  (Combined PEM)")
    print("\n[+] Django HTTPS serverni ishga tushirish mumkin\n")
    
    return True

if __name__ == "__main__":
    generate_ssl_certificate()
