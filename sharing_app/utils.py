from cryptography.fernet import Fernet
from django.conf import settings
import os


def get_fernet():
    """
    Load Fernet encryption key from Django settings.
    Raise error if missing.
    """
    key = getattr(settings, 'FERNET_KEY', None)
    if not key:
        raise RuntimeError("❌ FERNET_KEY is not configured in settings.py")
    return Fernet(key.encode())


def encrypt_bytes(data: bytes) -> bytes:
    """
    Encrypt in-memory bytes using Fernet.
    """
    f = get_fernet()
    return f.encrypt(data)


def decrypt_bytes(data: bytes) -> bytes:
    """
    Decrypt in-memory bytes using Fernet.
    """
    f = get_fernet()
    return f.decrypt(data)


def encrypt_file(file_path: str) -> bool:
    """
    Encrypt a file on disk using Fernet.
    """
    if not os.path.exists(file_path):
        return False

    with open(file_path, 'rb') as f:
        plaintext = f.read()

    fernet = get_fernet()
    ciphertext = fernet.encrypt(plaintext)

    with open(file_path, 'wb') as f:
        f.write(ciphertext)

    return True


def decrypt_file(file_path: str) -> bytes | None:
    """
    Decrypt and return file bytes.
    """
    if not os.path.exists(file_path):
        return None

    with open(file_path, 'rb') as f:
        encrypted_data = f.read()

    try:
        fernet = get_fernet()
        return fernet.decrypt(encrypted_data)
    except Exception:
        return None
