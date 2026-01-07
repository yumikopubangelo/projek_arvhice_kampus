from passlib.context import CryptContext
from passlib.exc import UnknownHashError


# =====================================================
# PASSWORD HASHING CONTEXT
# =====================================================
# Support both bcrypt and pbkdf2_sha256 for backward compatibility
pwd_context = CryptContext(schemes=["bcrypt", "pbkdf2_sha256"], deprecated="auto")


# =====================================================
# PASSWORD UTILITIES
# =====================================================

def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        str: Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except UnknownHashError:
        # If hash format is unknown, treat as invalid
        return False


def is_password_strong(password: str) -> tuple[bool, list[str]]:
    """
    Check if a password meets strength requirements.

    Args:
        password: Password to check

    Returns:
        tuple: (is_strong: bool, issues: list[str])
    """
    issues = []

    if len(password) < 8:
        issues.append("Password must be at least 8 characters long")

    if not any(char.isupper() for char in password):
        issues.append("Password must contain at least one uppercase letter")

    if not any(char.islower() for char in password):
        issues.append("Password must contain at least one lowercase letter")

    if not any(char.isdigit() for char in password):
        issues.append("Password must contain at least one digit")

    # Optional: Check for special characters
    # if not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?" for char in password):
    #     issues.append("Password must contain at least one special character")

    return len(issues) == 0, issues


# =====================================================
# LEGACY SUPPORT (if needed)
# =====================================================

def get_password_hash(password: str) -> str:
    """
    Alias for hash_password for backward compatibility.
    """
    return hash_password(password)


def check_password_hash(plain_password: str, hashed_password: str) -> bool:
    """
    Alias for verify_password for backward compatibility.
    """
    return verify_password(plain_password, hashed_password)