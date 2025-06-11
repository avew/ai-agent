"""
Document model for the Chat Agent application.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Document:
    """Document model representing uploaded files."""
    
    id: Optional[int] = None
    filename: str = ""
    filepath: str = ""
    checksum: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self):
        """Convert document to dictionary."""
        return {
            "id": self.id,
            "filename": self.filename,
            "filepath": self.filepath,
            "checksum": self.checksum,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create document from dictionary."""
        return cls(
            id=data.get("id"),
            filename=data.get("filename", ""),
            filepath=data.get("filepath", ""),
            checksum=data.get("checksum", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )


@dataclass
class DocumentChunk:
    """Document chunk model representing chunked text with embeddings."""
    
    id: Optional[int] = None
    document_id: int = 0
    chunk_index: int = 0
    content: str = ""
    embedding: Optional[List[float]] = None
    token_count: int = 0
    start_char: int = 0
    end_char: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self):
        """Convert document chunk to dictionary."""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "chunk_index": self.chunk_index,
            "content": self.content,
            "token_count": self.token_count,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create document chunk from dictionary."""
        return cls(
            id=data.get("id"),
            document_id=data.get("document_id", 0),
            chunk_index=data.get("chunk_index", 0),
            content=data.get("content", ""),
            embedding=data.get("embedding"),
            token_count=data.get("token_count", 0),
            start_char=data.get("start_char", 0),
            end_char=data.get("end_char", 0),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )


@dataclass
class SearchResult:
    """Search result model for RAG functionality."""
    
    content: str
    filename: str
    distance: float
    chunk_index: int = 0
    
    def to_dict(self):
        """Convert search result to dictionary."""
        return {
            "content": self.content,
            "filename": self.filename,
            "distance": self.distance,
            "chunk_index": self.chunk_index,
        }
