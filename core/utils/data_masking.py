import base64
import hashlib
from typing import Optional

from cryptography.fernet import Fernet
from core.config.settings import settings

SECRET_KEY = settings.SECRET_KEY



def get_encryption_key():
    # Use SHA-256 to get a 32-byte key from the SECRET_KEY
    key_hash = hashlib.sha256(SECRET_KEY.encode()).digest()
    return base64.urlsafe_b64encode(key_hash)


_cipher = Fernet(get_encryption_key())


def encrypt_data(data: Optional[str]) -> Optional[str]:
    """Encrypt sensitive data."""
    if not data:
        return data
    return _cipher.encrypt(data.encode()).decode()


def decrypt_data(encrypted_data: Optional[str]) -> Optional[str]:
    """Decrypt sensitive data."""
    if not encrypted_data:
        return encrypted_data
    try:
        return _cipher.decrypt(encrypted_data.encode()).decode()
    except Exception:
        return encrypted_data


def mask_generic(value: Optional[str], keep_last: int = 4) -> Optional[str]:
    """Mask all but the last N characters."""
    if not value:
        return value
    if len(value) <= keep_last:
        return value
    return ("X" * (len(value) - keep_last)) + value[-keep_last:]


def mask_email(value: Optional[str]) -> Optional[str]:
    """Mask email prefix."""
    if not value:
        return value
    if "@" not in value:
        return mask_generic(value)

    prefix, domain = value.split("@", 1)
    if len(prefix) <= 2:
        return "*" * len(prefix) + "@" + domain

    return prefix[0] + ("*" * (len(prefix) - 2)) + prefix[-1] + "@" + domain

