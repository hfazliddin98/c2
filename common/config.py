"""
Umumiy konfiguratsiya sozlamalari
"""

# Server sozlamalari
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8080
SECRET_KEY = "c2_platform_secret_key_2025"

# Xavfsizlik sozlamalari
ENCRYPTION_KEY_SIZE = 32
MAX_PAYLOAD_SIZE = 1024 * 1024  # 1MB

# Agent sozlamalari
HEARTBEAT_INTERVAL = 30  # sekund
RECONNECT_DELAY = 5  # sekund
MAX_RETRIES = 5

# Komanda turlari
COMMAND_TYPES = {
    "SYSTEM_INFO": "sysinfo",
    "EXECUTE_CMD": "exec",
    "FILE_UPLOAD": "upload",
    "FILE_DOWNLOAD": "download",
    "SCREENSHOT": "screenshot",
    "HEARTBEAT": "heartbeat",
    "SHELL": "shell"
}

# Response kodlari
RESPONSE_CODES = {
    "SUCCESS": 200,
    "ERROR": 500,
    "NOT_FOUND": 404,
    "UNAUTHORIZED": 401
}