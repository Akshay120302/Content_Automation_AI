"""
Password strength validation utilities
"""
import re
from typing import Tuple


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password strength with comprehensive checks
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 72:
        return False, "Password must not exceed 72 characters (bcrypt limit)"
    
    # Check for uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    # Check for special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/`~;]', password):
        return False, "Password must contain at least one special character (!@#$%^&* etc.)"
    
    # Check for common weak passwords
    weak_passwords = [
        'password', 'password123', '12345678', 'qwerty123',
        'admin123', 'welcome123', 'letmein123', 'monkey123'
    ]
    if password.lower() in weak_passwords:
        return False, "This password is too common. Please choose a stronger password"
    
    return True, ""


def get_password_requirements() -> str:
    """Get a user-friendly string of password requirements"""
    return (
        "Password must:\n"
        "  • Be 8-72 characters long\n"
        "  • Contain uppercase letter (A-Z)\n"
        "  • Contain lowercase letter (a-z)\n"
        "  • Contain number (0-9)\n"
        "  • Contain special character (!@#$%^&* etc.)"
    )
