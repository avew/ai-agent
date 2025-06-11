"""
Document model for the Chat Agent application.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Document:
    """Document model representing uploaded files with embeddings."""
    
    id: Optional[int] = None
    filename: str = ""
    content: str = ""
    embedding: Optional[List[float]] = None
    filepath: str = ""
    checksum: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self):
        """Convert document to dictionary."""
        return {
            "id": self.id,
            "filename": self.filename,
            "content": self.content,
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
            content=data.get("content", ""),
            embedding=data.get("embedding"),
            filepath=data.get("filepath", ""),
            checksum=data.get("checksum", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )


@dataclass
class SearchResult:
    """Search result model for RAG functionality."""
    
    content: str
    filename: str
    distance: float
    
    def to_dict(self):
        """Convert search result to dictionary."""
        return {
            "content": self.content,
            "filename": self.filename,
            "distance": self.distance,
        }
