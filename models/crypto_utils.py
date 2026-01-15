import base64
import hashlib
from cryptography.fernet import Fernet

def hill_key_to_fernet_key(hill_key_base64: str) -> bytes:
    # Hash SHA-256 → 32 bytes
    digest = hashlib.sha256(hill_key_base64.encode()).digest()
    # Fernet attend du base64 urlsafe
    return base64.urlsafe_b64encode(digest)
def encrypt_file_bytes(file_bytes: bytes, hill_key_base64: str) -> bytes:
    fernet_key = hill_key_to_fernet_key(hill_key_base64)
    fernet = Fernet(fernet_key)
    return fernet.encrypt(file_bytes)

def decrypt_file_bytes(enc_bytes: bytes, hill_key_base64: str) -> bytes:
    fernet_key = hill_key_to_fernet_key(hill_key_base64)
    fernet = Fernet(fernet_key)
    return fernet.decrypt(enc_bytes)
