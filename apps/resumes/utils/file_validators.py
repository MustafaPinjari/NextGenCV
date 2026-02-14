"""
File validation utilities for secure PDF upload handling.

This module provides:
- PDF file type and size validation
- Embedded script detection
- Secure filename generation
"""

import os
import re
import uuid
import logging
import mimetypes
from typing import Tuple, Optional
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


# Maximum file size: 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes

# Allowed MIME types
ALLOWED_MIME_TYPES = ['application/pdf']

# Allowed file extensions
ALLOWED_EXTENSIONS = ['.pdf']


def validate_pdf_file(file) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded PDF file with type and size checks.
    
    Performs the following validations:
    1. File extension check (.pdf only)
    2. MIME type verification (application/pdf)
    3. File size check (max 10MB)
    4. Basic file integrity check
    
    Args:
        file: Django UploadedFile object
        
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
        
    Example:
        >>> is_valid, error = validate_pdf_file(uploaded_file)
        >>> if not is_valid:
        >>>     raise ValidationError(error)
    """
    # 1. Check file extension
    file_name = file.name.lower()
    file_ext = os.path.splitext(file_name)[1]
    
    if file_ext not in ALLOWED_EXTENSIONS:
        return False, f"Invalid file extension '{file_ext}'. Only PDF files are allowed."
    
    # 2. Check MIME type
    # First, try to get MIME type from the file object
    mime_type = file.content_type
    
    # Fallback: guess MIME type from filename
    if not mime_type or mime_type == 'application/octet-stream':
        guessed_type, _ = mimetypes.guess_type(file_name)
        if guessed_type:
            mime_type = guessed_type
    
    if mime_type not in ALLOWED_MIME_TYPES:
        return False, f"Invalid file type '{mime_type}'. Only PDF files (application/pdf) are allowed."
    
    # 3. Check file size
    file_size = file.size
    if file_size > MAX_FILE_SIZE:
        size_mb = file_size / (1024 * 1024)
        max_mb = MAX_FILE_SIZE / (1024 * 1024)
        return False, f"File size ({size_mb:.2f}MB) exceeds maximum allowed size ({max_mb}MB)."
    
    # 4. Check if file is empty
    if file_size == 0:
        return False, "Uploaded file is empty."
    
    # 5. Basic PDF header check
    # PDF files should start with "%PDF-"
    try:
        file.seek(0)
        header = file.read(5)
        file.seek(0)  # Reset file pointer
        
        if header != b'%PDF-':
            return False, "File does not appear to be a valid PDF (invalid header)."
    except Exception as e:
        logger.warning(f"Could not read file header: {e}")
        # Don't fail validation if we can't read header
        # The PDF parser will catch actual corruption
    
    return True, None


def has_embedded_scripts(file) -> bool:
    """
    Scan PDF file for potentially malicious embedded scripts.
    
    This is a basic scanner that looks for common JavaScript patterns
    in PDF files. PDFs can contain JavaScript that could be malicious.
    
    Detection patterns:
    - /JavaScript keyword
    - /JS keyword
    - /OpenAction (auto-execute)
    - /AA (additional actions)
    - /Launch (execute external programs)
    
    Args:
        file: Django UploadedFile object
        
    Returns:
        bool: True if suspicious content detected, False otherwise
        
    Note:
        This is a basic heuristic check. For production systems,
        consider using dedicated PDF security scanning tools.
    """
    try:
        file.seek(0)
        content = file.read()
        file.seek(0)  # Reset file pointer
        
        # Convert to string for pattern matching (handle encoding errors)
        try:
            content_str = content.decode('latin-1')  # PDF uses latin-1 encoding
        except UnicodeDecodeError:
            # If we can't decode, treat as binary and search for byte patterns
            content_str = str(content)
        
        # Suspicious patterns in PDFs
        suspicious_patterns = [
            r'/JavaScript',
            r'/JS\s',
            r'/OpenAction',
            r'/AA\s',  # Additional Actions
            r'/Launch',
            r'/SubmitForm',
            r'/ImportData',
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, content_str, re.IGNORECASE):
                logger.warning(f"Suspicious pattern detected in PDF: {pattern}")
                return True
        
        # Check for suspicious JavaScript functions
        js_patterns = [
            r'eval\s*\(',
            r'unescape\s*\(',
            r'String\.fromCharCode',
        ]
        
        for pattern in js_patterns:
            if re.search(pattern, content_str, re.IGNORECASE):
                logger.warning(f"Suspicious JavaScript pattern detected: {pattern}")
                return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error scanning file for embedded scripts: {e}")
        # If we can't scan, err on the side of caution
        return True


def secure_filename_generator(original_filename: str, user_id: Optional[int] = None) -> str:
    """
    Generate a secure random filename for uploaded files.
    
    This prevents:
    - Path traversal attacks (../)
    - Filename collisions
    - Information disclosure (original filename not stored)
    
    The generated filename format:
    - Uses UUID4 for randomness
    - Preserves original file extension
    - Optionally includes user_id for organization
    
    Args:
        original_filename: Original uploaded filename
        user_id: Optional user ID for organizing files
        
    Returns:
        str: Secure filename
        
    Example:
        >>> secure_filename_generator("my resume.pdf", user_id=123)
        'user_123_a1b2c3d4-e5f6-7890-abcd-ef1234567890.pdf'
    """
    # Extract file extension
    _, ext = os.path.splitext(original_filename)
    ext = ext.lower()
    
    # Validate extension
    if ext not in ALLOWED_EXTENSIONS:
        ext = '.pdf'  # Default to .pdf
    
    # Generate random UUID
    random_uuid = uuid.uuid4()
    
    # Build secure filename
    if user_id:
        secure_name = f"user_{user_id}_{random_uuid}{ext}"
    else:
        secure_name = f"{random_uuid}{ext}"
    
    return secure_name


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing potentially dangerous characters.
    
    This is used when we need to preserve some aspect of the original
    filename but make it safe.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove path components
    filename = os.path.basename(filename)
    
    # Remove or replace dangerous characters
    # Keep only alphanumeric, dash, underscore, and dot
    filename = re.sub(r'[^\w\s.-]', '', filename)
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    # Remove multiple consecutive dots (path traversal attempt)
    filename = re.sub(r'\.{2,}', '.', filename)
    
    # Limit length
    name, ext = os.path.splitext(filename)
    if len(name) > 100:
        name = name[:100]
    
    return name + ext


def get_file_storage_path(user_id: int, filename: str) -> str:
    """
    Generate a secure storage path for uploaded files.
    
    Files are organized by user ID to:
    - Prevent filename collisions
    - Enable easy cleanup on user deletion
    - Organize files logically
    
    Args:
        user_id: User ID
        filename: Secure filename (from secure_filename_generator)
        
    Returns:
        str: Relative path for file storage
        
    Example:
        >>> get_file_storage_path(123, "uuid.pdf")
        'uploads/user_123/uuid.pdf'
    """
    return os.path.join('uploads', f'user_{user_id}', filename)


def validate_and_prepare_upload(file, user_id: int) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Complete validation and preparation pipeline for file upload.
    
    This is a convenience function that combines all validation steps
    and generates a secure filename and path.
    
    Args:
        file: Django UploadedFile object
        user_id: User ID for file organization
        
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str], storage_path: Optional[str])
        
    Example:
        >>> is_valid, error, path = validate_and_prepare_upload(file, user.id)
        >>> if is_valid:
        >>>     # Save file to path
        >>>     pass
    """
    # Step 1: Validate file
    is_valid, error = validate_pdf_file(file)
    if not is_valid:
        return False, error, None
    
    # Step 2: Check for embedded scripts
    if has_embedded_scripts(file):
        return False, "File contains potentially malicious content and cannot be uploaded.", None
    
    # Step 3: Generate secure filename
    secure_name = secure_filename_generator(file.name, user_id)
    
    # Step 4: Generate storage path
    storage_path = get_file_storage_path(user_id, secure_name)
    
    return True, None, storage_path
