"""
Text sanitization utilities for security.

This module provides comprehensive text sanitization to prevent:
- XSS (Cross-Site Scripting) attacks
- SQL injection (handled by Django ORM, but extra layer)
- Control character injection
- HTML injection

All user input and extracted text should be sanitized using these utilities.
"""

import re
import bleach
import logging
from typing import Optional

logger = logging.getLogger(__name__)


# Allowed HTML tags for rich text (if needed in future)
# Currently we strip all HTML for maximum security
ALLOWED_TAGS = []
ALLOWED_ATTRIBUTES = {}


def sanitize_html(text: str) -> str:
    """
    Remove all HTML tags and attributes from text.
    
    This prevents XSS attacks by stripping all HTML.
    Uses bleach library for robust HTML sanitization.
    
    Args:
        text: Input text that may contain HTML
        
    Returns:
        str: Text with all HTML removed
        
    Example:
        >>> sanitize_html("<script>alert('xss')</script>Hello")
        "Hello"
    """
    if not text:
        return ""
    
    # Strip all HTML tags
    cleaned = bleach.clean(
        text,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )
    
    return cleaned


def remove_control_characters(text: str) -> str:
    """
    Remove control characters from text.
    
    Control characters can cause issues in:
    - Database storage
    - Text rendering
    - Log files
    - Export formats
    
    Preserves:
    - Newlines (\n)
    - Tabs (\t)
    - Carriage returns (\r)
    
    Args:
        text: Input text
        
    Returns:
        str: Text with control characters removed
    """
    if not text:
        return ""
    
    # Remove control characters except newlines and tabs
    cleaned = ''.join(
        char for char in text
        if char.isprintable() or char in ['\n', '\t', '\r']
    )
    
    return cleaned


def sanitize_filename(filename: str) -> str:
    r"""
    Sanitize filename to prevent path traversal and other attacks.
    
    Removes:
    - Path separators (/, \)
    - Parent directory references (..)
    - Special characters
    
    Args:
        filename: Original filename
        
    Returns:
        str: Safe filename
        
    Example:
        >>> sanitize_filename("../../etc/passwd")
        "etcpasswd"
    """
    if not filename:
        return "unnamed"
    
    # Remove path components
    import os
    filename = os.path.basename(filename)
    
    # Remove dangerous characters
    # Keep only alphanumeric, dash, underscore, and dot
    filename = re.sub(r'[^\w\s.-]', '', filename)
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    # Remove multiple consecutive dots (path traversal attempt)
    filename = re.sub(r'\.{2,}', '.', filename)
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        name = name[:255 - len(ext)]
        filename = name + ext
    
    # Ensure we have a valid filename
    if not filename or filename == '.':
        filename = "unnamed"
    
    return filename


def sanitize_user_input(text: str, max_length: Optional[int] = None) -> str:
    """
    Comprehensive sanitization for user input.
    
    Applies multiple sanitization steps:
    1. HTML sanitization
    2. Control character removal
    3. Whitespace normalization
    4. Length limiting
    
    Args:
        text: User input text
        max_length: Optional maximum length
        
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    # Step 1: Remove HTML
    text = sanitize_html(text)
    
    # Step 2: Remove control characters
    text = remove_control_characters(text)
    
    # Step 3: Normalize whitespace
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    
    # Replace multiple newlines with max 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Step 4: Trim
    text = text.strip()
    
    # Step 5: Limit length if specified
    if max_length and len(text) > max_length:
        text = text[:max_length]
        logger.warning(f"Text truncated to {max_length} characters")
    
    return text


def sanitize_extracted_pdf_text(text: str) -> str:
    """
    Sanitize text extracted from PDF files.
    
    PDFs can contain malicious content, so we apply
    comprehensive sanitization.
    
    Args:
        text: Text extracted from PDF
        
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    # Apply comprehensive sanitization
    text = sanitize_user_input(text)
    
    # Additional PDF-specific cleaning
    # Remove common PDF artifacts
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    return text


def sanitize_job_description(text: str) -> str:
    """
    Sanitize job description input.
    
    Job descriptions are user input that gets stored and
    used for analysis, so they need sanitization.
    
    Args:
        text: Job description text
        
    Returns:
        str: Sanitized job description
    """
    # Apply standard sanitization with length limit
    return sanitize_user_input(text, max_length=50000)


def sanitize_custom_css(css: str) -> str:
    r"""
    Sanitize custom CSS input.
    
    CSS can contain malicious code (e.g., expression(), url() with javascript:)
    This provides basic sanitization. For production, consider using
    a dedicated CSS sanitizer library.
    
    Args:
        css: Custom CSS code
        
    Returns:
        str: Sanitized CSS
    """
    if not css:
        return ""
    
    # Remove potentially dangerous CSS patterns
    dangerous_patterns = [
        r'javascript:',
        r'expression\s*\(',
        r'@import',
        r'behavior:',
        r'-moz-binding:',
    ]
    
    for pattern in dangerous_patterns:
        css = re.sub(pattern, '', css, flags=re.IGNORECASE)
    
    # Limit length
    if len(css) > 10000:
        css = css[:10000]
        logger.warning("Custom CSS truncated to 10000 characters")
    
    return css


def validate_url(url: str) -> bool:
    """
    Validate URL to prevent malicious URLs.
    
    Checks for:
    - Valid URL format
    - Safe protocols (http, https)
    - No javascript: or data: URLs
    
    Args:
        url: URL to validate
        
    Returns:
        bool: True if URL is safe
    """
    if not url:
        return True  # Empty URL is okay
    
    # Check for dangerous protocols
    dangerous_protocols = ['javascript:', 'data:', 'file:', 'vbscript:']
    url_lower = url.lower().strip()
    
    for protocol in dangerous_protocols:
        if url_lower.startswith(protocol):
            logger.warning(f"Dangerous URL protocol detected: {protocol}")
            return False
    
    # URL should start with http:// or https:// or be relative
    if not (url_lower.startswith('http://') or 
            url_lower.startswith('https://') or 
            url_lower.startswith('/')):
        logger.warning(f"Invalid URL format: {url}")
        return False
    
    return True


# Convenience function for sanitizing all resume data
def sanitize_resume_data(data: dict) -> dict:
    """
    Sanitize all text fields in resume data dictionary.
    
    This is a convenience function to sanitize entire resume
    data structures at once.
    
    Args:
        data: Dictionary containing resume data
        
    Returns:
        dict: Sanitized resume data
    """
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            # Sanitize string values
            sanitized[key] = sanitize_user_input(value)
        elif isinstance(value, dict):
            # Recursively sanitize nested dicts
            sanitized[key] = sanitize_resume_data(value)
        elif isinstance(value, list):
            # Sanitize list items
            sanitized[key] = [
                sanitize_user_input(item) if isinstance(item, str)
                else sanitize_resume_data(item) if isinstance(item, dict)
                else item
                for item in value
            ]
        else:
            # Keep other types as-is
            sanitized[key] = value
    
    return sanitized
