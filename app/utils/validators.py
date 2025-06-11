"""
Validation utilities for the Chat Agent application.
"""
from flask import current_app
from typing import Any, Dict, List, Optional


def validate_file_upload(file) -> Dict[str, Any]:
    """
    Validate uploaded file.
    
    Args:
        file: Uploaded file object
        
    Returns:
        Dictionary with validation result and error message if any
    """
    if not file:
        return {"valid": False, "error": "No file provided"}
    
    if file.filename == '':
        return {"valid": False, "error": "No file selected"}
    
    # Check file extension
    allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
    if not is_allowed_file_extension(file.filename, allowed_extensions):
        return {
            "valid": False, 
            "error": f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        }
    
    return {"valid": True, "error": None}


def validate_chat_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate chat request data.
    
    Args:
        data: Request data dictionary
        
    Returns:
        Dictionary with validation result and error message if any
    """
    if not data:
        return {"valid": False, "error": "No data provided"}
    
    query = data.get("query")
    if not query:
        return {"valid": False, "error": "Query is required"}
    
    if not isinstance(query, str):
        return {"valid": False, "error": "Query must be a string"}
    
    if len(query.strip()) == 0:
        return {"valid": False, "error": "Query cannot be empty"}
    
    if len(query) > 1000:  # Reasonable limit
        return {"valid": False, "error": "Query too long (max 1000 characters)"}
    
    return {"valid": True, "error": None}


def is_allowed_file_extension(filename: str, allowed_extensions: set) -> bool:
    """
    Check if file extension is allowed.
    
    Args:
        filename: Name of the file
        allowed_extensions: Set of allowed file extensions
        
    Returns:
        True if file extension is allowed, False otherwise
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def validate_pagination_params(page: Optional[str], per_page: Optional[str]) -> Dict[str, Any]:
    """
    Validate pagination parameters.
    
    Args:
        page: Page number as string
        per_page: Items per page as string
        
    Returns:
        Dictionary with validated parameters or error
    """
    try:
        page_num = int(page) if page else 1
        per_page_num = int(per_page) if per_page else 10
        
        if page_num < 1:
            return {"valid": False, "error": "Page number must be greater than 0"}
        
        if per_page_num < 1 or per_page_num > 100:
            return {"valid": False, "error": "Items per page must be between 1 and 100"}
        
        return {
            "valid": True,
            "page": page_num,
            "per_page": per_page_num,
            "error": None
        }
    
    except ValueError:
        return {"valid": False, "error": "Invalid pagination parameters"}


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and other issues.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    import os
    
    # Remove path separators
    filename = filename.replace('/', '_').replace('\\', '_')
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename
