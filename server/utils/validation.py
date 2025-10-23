"""
Input validation utilities for security
"""
import re
from typing import Optional, Union
from constants import (
    MAX_PHONE_NUMBER_LENGTH,
    MAX_NAME_LENGTH,
    ERROR_PHONE_NUMBER_TOO_LONG,
    ERROR_NAME_TOO_LONG,
    ERROR_NAME_IS_DIGIT
)


def validate_phone_number(phone_number: str) -> tuple[bool, Optional[str]]:
    """
    Validate phone number format and length
    
    Args:
        phone_number: Phone number to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not phone_number:
        return False, "Phone number is required"
    
    if len(phone_number) > MAX_PHONE_NUMBER_LENGTH:
        return False, ERROR_PHONE_NUMBER_TOO_LONG
    
    # Remove any non-digit characters for validation
    digits_only = re.sub(r'[^\d]', '', phone_number)
    
    # Check if it's a valid phone number format (at least 7 digits)
    if len(digits_only) < 7 or len(digits_only) > 15:
        return False, "Invalid phone number format"
    
    return True, None


def validate_name(name: str) -> tuple[bool, Optional[str]]:
    """
    Validate name format and length
    
    Args:
        name: Name to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not name:
        return False, "Name is required"
    
    if len(name.strip()) == 0:
        return False, "Name cannot be empty"
    
    if len(name) > MAX_NAME_LENGTH:
        return False, ERROR_NAME_TOO_LONG
    
    # Check if name contains only digits
    if name.strip().isdigit():
        return False, ERROR_NAME_IS_DIGIT
    
    # Check for potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`', '$']
    if any(char in name for char in dangerous_chars):
        return False, "Name contains invalid characters"
    
    return True, None


def validate_amount(amount: Union[str, int, float]) -> tuple[bool, Optional[str]]:
    """
    Validate amount value
    
    Args:
        amount: Amount to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if amount is None:
        return False, "Amount is required"
    
    try:
        amount_float = float(amount)
        
        if amount_float <= 0:
            return False, "Amount must be greater than 0"
        
        if amount_float > 999999999:  # Reasonable upper limit
            return False, "Amount is too large"
        
        return True, None
        
    except (ValueError, TypeError):
        return False, "Invalid amount format"


def sanitize_input(input_string: str) -> str:
    """
    Sanitize input string to prevent injection attacks
    
    Args:
        input_string: String to sanitize
        
    Returns:
        str: Sanitized string
    """
    if not input_string:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\';()&|`$\\]', '', input_string)
    
    # Limit length to prevent buffer overflow
    return sanitized[:1000]


def validate_request_id(request_id: Union[str, int]) -> tuple[bool, Optional[str]]:
    """
    Validate request ID
    
    Args:
        request_id: Request ID to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if request_id is None:
        return False, "Request ID is required"
    
    try:
        request_id_int = int(request_id)
        
        if request_id_int <= 0:
            return False, "Invalid request ID"
        
        return True, None
        
    except (ValueError, TypeError):
        return False, "Invalid request ID format"


def validate_contact_id(contact_id: Union[str, int]) -> tuple[bool, Optional[str]]:
    """
    Validate contact ID
    
    Args:
        contact_id: Contact ID to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if contact_id is None:
        return False, "Contact ID is required"
    
    try:
        contact_id_int = int(contact_id)
        
        if contact_id_int <= 0:
            return False, "Invalid contact ID"
        
        return True, None
        
    except (ValueError, TypeError):
        return False, "Invalid contact ID format"
