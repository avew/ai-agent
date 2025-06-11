"""
File utilities for document processing.
"""
import os
import hashlib
import tempfile
import pandas as pd
from PyPDF2 import PdfReader
from docx import Document as DocxDocument
from typing import BinaryIO


def extract_text(file: BinaryIO, filename: str) -> str:
    """
    Extract text content from uploaded files.
    
    Args:
        file: File object to extract text from
        filename: Name of the file to determine extraction method
        
    Returns:
        Extracted text content
        
    Raises:
        ValueError: If file type is not supported
    """
    ext = filename.split('.')[-1].lower()
    
    if ext == 'pdf':
        reader = PdfReader(file)
        return '\n'.join(page.extract_text() for page in reader.pages if page.extract_text())
    
    elif ext == 'txt':
        return file.read().decode('utf-8')
    
    elif ext == 'docx':
        doc = DocxDocument(file)
        return '\n'.join([p.text for p in doc.paragraphs])
    
    elif ext in ('xls', 'xlsx'):
        df = pd.read_excel(file)
        return df.to_string(index=False)
    
    else:
        raise ValueError(f'Unsupported file type: {ext}')


def get_file_checksum(file_path: str) -> str:
    """
    Calculate SHA-256 checksum of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        SHA-256 checksum as hexadecimal string
    """
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def is_allowed_file(filename: str, allowed_extensions: set) -> bool:
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


def save_uploaded_file(file, upload_folder: str, filename: str) -> str:
    """
    Save uploaded file to specified folder.
    
    Args:
        file: File object to save
        upload_folder: Directory to save the file
        filename: Name to save the file as
        
    Returns:
        Full path to the saved file
    """
    # Ensure upload folder exists
    os.makedirs(upload_folder, exist_ok=True)
    
    # Create full path
    file_path = os.path.join(upload_folder, filename)
    
    # Save file
    file.save(file_path)
    
    return file_path
