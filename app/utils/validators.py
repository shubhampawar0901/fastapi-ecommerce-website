"""
Validation utilities for data validation
Common validation functions used across the application
"""

import re
from typing import Optional
from email_validator import validate_email as email_validate, EmailNotValidError


def validate_email(email: str) -> bool:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email is valid, False otherwise
    """
    try:
        email_validate(email)
        return True
    except EmailNotValidError:
        return False


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format
    Supports international formats
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if phone is valid, False otherwise
    """
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Check if it matches international format
    pattern = r'^\+?[1-9]\d{1,14}$'
    return bool(re.match(pattern, cleaned))


def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return False, "Password must be less than 128 characters long"
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for at least one digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, None


def validate_slug(slug: str) -> bool:
    """
    Validate URL slug format
    
    Args:
        slug: Slug to validate
        
    Returns:
        True if slug is valid, False otherwise
    """
    # Slug should contain only lowercase letters, numbers, and hyphens
    pattern = r'^[a-z0-9-]+$'
    return bool(re.match(pattern, slug)) and len(slug) <= 100


def validate_sku(sku: str) -> bool:
    """
    Validate product SKU format
    
    Args:
        sku: SKU to validate
        
    Returns:
        True if SKU is valid, False otherwise
    """
    # SKU should contain only alphanumeric characters and hyphens
    pattern = r'^[A-Z0-9-]+$'
    return bool(re.match(pattern, sku.upper())) and len(sku) <= 50
