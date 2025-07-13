"""
Helper utilities for common operations
General purpose helper functions
"""

import re
import unicodedata
from typing import Optional
from decimal import Decimal


def generate_slug(text: str) -> str:
    """
    Generate URL-friendly slug from text
    
    Args:
        text: Text to convert to slug
        
    Returns:
        URL-friendly slug
    """
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove non-alphanumeric characters except spaces and hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    
    # Replace spaces and multiple hyphens with single hyphen
    text = re.sub(r'[-\s]+', '-', text)
    
    # Remove leading/trailing hyphens
    text = text.strip('-')
    
    return text[:100]  # Limit length


def format_currency(amount: Decimal, currency: str = "USD") -> str:
    """
    Format decimal amount as currency string
    
    Args:
        amount: Amount to format
        currency: Currency code (default: USD)
        
    Returns:
        Formatted currency string
    """
    if currency.upper() == "USD":
        return f"${amount:.2f}"
    elif currency.upper() == "EUR":
        return f"€{amount:.2f}"
    elif currency.upper() == "GBP":
        return f"£{amount:.2f}"
    else:
        return f"{amount:.2f} {currency.upper()}"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path separators and other dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Replace spaces with underscores
    filename = re.sub(r'\s+', '_', filename)
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        max_name_length = 255 - len(ext) - 1 if ext else 255
        filename = name[:max_name_length] + ('.' + ext if ext else '')
    
    return filename


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to specified length with suffix
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def parse_sort_param(sort_param: Optional[str], allowed_fields: list[str]) -> tuple[str, str]:
    """
    Parse sort parameter into field and direction
    
    Args:
        sort_param: Sort parameter (e.g., "name", "-created_at")
        allowed_fields: List of allowed sort fields
        
    Returns:
        Tuple of (field, direction)
    """
    if not sort_param:
        return "id", "asc"
    
    direction = "desc" if sort_param.startswith("-") else "asc"
    field = sort_param.lstrip("-")
    
    if field not in allowed_fields:
        return "id", "asc"
    
    return field, direction
