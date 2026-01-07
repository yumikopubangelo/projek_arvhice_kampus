from cryptography.fernet import Fernet
import base64
import os
from app.config import get_settings

settings = get_settings()

# =====================================================
# ENCRYPTION CONFIGURATION
# =====================================================
# Use the same key as frontend for compatibility
ENCRYPTION_KEY = settings.ENCRYPTION_KEY or "campus-archive-secret-key-2024"

# Create Fernet key from string
def _get_fernet_key():
    """Convert string key to Fernet-compatible key"""
    key = ENCRYPTION_KEY.encode()
    # Pad or truncate to 32 bytes for Fernet
    if len(key) < 32:
        key = key.ljust(32, b'\0')
    elif len(key) > 32:
        key = key[:32]
    return base64.urlsafe_b64encode(key)

fernet = Fernet(_get_fernet_key())

# =====================================================
# ENCRYPTION FUNCTIONS
# =====================================================

def encrypt_data(data: str) -> str:
    """
    Encrypt sensitive data
    Args:
        data: Plain text data to encrypt
    Returns:
        str: Encrypted data as base64 string
    """
    try:
        encrypted = fernet.encrypt(data.encode())
        return encrypted.decode()
    except Exception as e:
        raise ValueError(f"Encryption failed: {str(e)}")

def decrypt_data(encrypted_data: str) -> str:
    """
    Decrypt sensitive data
    Args:
        encrypted_data: Encrypted data as base64 string
    Returns:
        str: Decrypted plain text
    """
    try:
        decrypted = fernet.decrypt(encrypted_data.encode())
        return decrypted.decode()
    except Exception as e:
        # If decryption fails, return original (might not be encrypted)
        return encrypted_data

def decrypt_sensitive_fields(data: dict, sensitive_fields: list = None) -> dict:
    """
    Decrypt sensitive fields in a dictionary
    Args:
        data: Dictionary containing potentially encrypted fields
        sensitive_fields: List of field names to decrypt (default: common sensitive fields)
    Returns:
        dict: Dictionary with sensitive fields decrypted
    """
    if sensitive_fields is None:
        sensitive_fields = ['password', 'student_id', 'phone']

    decrypted_data = data.copy()

    for field in sensitive_fields:
        if field in decrypted_data and isinstance(decrypted_data[field], str):
            decrypted_data[field] = decrypt_data(decrypted_data[field])

    return decrypted_data

def encrypt_sensitive_fields(data: dict, sensitive_fields: list = None) -> dict:
    """
    Encrypt sensitive fields in a dictionary
    Args:
        data: Dictionary containing fields to encrypt
        sensitive_fields: List of field names to encrypt
    Returns:
        dict: Dictionary with sensitive fields encrypted
    """
    if sensitive_fields is None:
        sensitive_fields = ['password', 'student_id', 'phone']

    encrypted_data = data.copy()

    for field in sensitive_fields:
        if field in encrypted_data and isinstance(encrypted_data[field], str):
            encrypted_data[field] = encrypt_data(encrypted_data[field])

    return encrypted_data