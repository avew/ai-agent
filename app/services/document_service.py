"""
Document service for handling document operations.
"""
import os
from flask import current_app
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from typing import List, Optional, Dict, Any

from ..models import Document, DocumentChunk
from ..utils import extract_text, get_file_checksum, save_uploaded_file, sanitize_filename
from .embedding_service import EmbeddingService


class DocumentService:
    """Service for managing document operations."""
    
    def __init__(self):
        self.engine = create_engine(current_app.config['DATABASE_URL'], poolclass=NullPool)
        self.embedding_service = EmbeddingService()
        self.upload_folder = current_app.config['UPLOAD_FOLDER']
    
    def upload_document(self, file, filename: str) -> Dict[str, Any]:
        """
        Upload and process a document.
        
        Args:
            file: Uploaded file object
            filename: Original filename
            
        Returns:
            Dictionary with upload result
        """
        try:
            # Sanitize filename
            safe_filename = sanitize_filename(filename)
            
            # Save file
            file_path = save_uploaded_file(file, self.upload_folder, safe_filename)
            
            # Calculate checksum
            checksum = get_file_checksum(file_path)
            
            # Check for duplicates
            if self._document_exists(checksum):
                os.remove(file_path)  # Remove duplicate file
                return {
                    "success": False,
                    "error": "Document with same content already exists",
                    "code": "DUPLICATE"
                }
            
            # Extract text content
            with open(file_path, "rb") as f:
                text_content = extract_text(f, safe_filename)
            
            if not text_content.strip():
                os.remove(file_path)
                return {
                    "success": False,
                    "error": "No content found in file",
                    "code": "EMPTY_CONTENT"
                }
            
            # Generate embeddings using chunking approach
            chunks = self.embedding_service.create_chunks(text_content)
            chunks_with_embeddings = self.embedding_service.get_embeddings_for_chunks(chunks)
            
            # Generate full document embedding for backward compatibility
            full_embedding = self.embedding_service.get_embedding(text_content[:8000])  # Truncate for safety
            embedding_str = self.embedding_service.format_embedding_for_db(full_embedding)
            
            # Save to database
            document_id = self._save_document_to_db(
                filename=safe_filename,
                content=text_content,
                embedding=embedding_str,
                filepath=file_path,
                checksum=checksum,
                chunks=chunks_with_embeddings
            )
            
            return {
                "success": True,
                "document_id": document_id,
                "filename": safe_filename,
                "filepath": file_path,
                "checksum": checksum
            }
            
        except Exception as e:
            current_app.logger.error(f"Error uploading document: {e}")
            # Clean up file if it was saved
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
            return {
                "success": False,
                "error": str(e),
                "code": "UPLOAD_ERROR"
            }
    
    def get_documents(self, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """
        Get paginated list of documents.
        
        Args:
            page: Page number (1-based)
            per_page: Items per page
            
        Returns:
            Dictionary with documents and pagination info
        """
        try:
            offset = (page - 1) * per_page
            
            with self.engine.connect() as conn:
                # Get total count
                count_result = conn.execute(text("SELECT COUNT(*) FROM documents")).fetchone()
                total = count_result[0] if count_result else 0
                
                # Get documents
                rows = conn.execute(text("""
                    SELECT id, filename, filepath, checksum, created_at, updated_at 
                    FROM documents 
                    ORDER BY created_at DESC 
                    LIMIT :limit OFFSET :offset
                """), {"limit": per_page, "offset": offset}).fetchall()
            
            documents = []
            for row in rows:
                documents.append({
                    "id": row.id,
                    "filename": row.filename,
                    "filepath": row.filepath,
                    "checksum": row.checksum,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "updated_at": row.updated_at.isoformat() if row.updated_at else None,
                    "download_url": f"/api/documents/{row.id}/download"
                })
            
            return {
                "success": True,
                "documents": documents,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "pages": (total + per_page - 1) // per_page
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting documents: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_document_by_id(self, document_id: int) -> Optional[Document]:
        """
        Get document by ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document object or None if not found
        """
        try:
            with self.engine.connect() as conn:
                row = conn.execute(text("""
                    SELECT id, filename, content, filepath, checksum, created_at, updated_at
                    FROM documents 
                    WHERE id = :id
                """), {"id": document_id}).fetchone()
            
            if row:
                return Document(
                    id=row.id,
                    filename=row.filename,
                    content=row.content,
                    filepath=row.filepath,
                    checksum=row.checksum,
                    created_at=row.created_at,
                    updated_at=row.updated_at
                )
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error getting document {document_id}: {e}")
            return None
    
    def get_document_chunks(self, document_id: int) -> List[DocumentChunk]:
        """
        Get all chunks for a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            List of DocumentChunk objects
        """
        try:
            with self.engine.connect() as conn:
                rows = conn.execute(text("""
                    SELECT id, document_id, chunk_index, content, token_count, 
                           start_char, end_char, created_at, updated_at
                    FROM document_chunks 
                    WHERE document_id = :document_id 
                    ORDER BY chunk_index ASC
                """), {"document_id": document_id}).fetchall()
            
            chunks = []
            for row in rows:
                chunks.append(DocumentChunk(
                    id=row.id,
                    document_id=row.document_id,
                    chunk_index=row.chunk_index,
                    content=row.content,
                    token_count=row.token_count,
                    start_char=row.start_char,
                    end_char=row.end_char,
                    created_at=row.created_at,
                    updated_at=row.updated_at
                ))
            
            return chunks
            
        except Exception as e:
            current_app.logger.error(f"Error getting chunks for document {document_id}: {e}")
            return []
    
    def delete_document(self, document_id: int) -> Dict[str, Any]:
        """
        Delete document by ID.
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            Dictionary with deletion result
        """
        try:
            with self.engine.begin() as conn:
                # Get document info first
                doc_row = conn.execute(text("""
                    SELECT filepath FROM documents WHERE id = :id
                """), {"id": document_id}).fetchone()
                
                if not doc_row:
                    return {
                        "success": False,
                        "error": "Document not found",
                        "code": "NOT_FOUND"
                    }
                
                # Delete file from storage
                if os.path.exists(doc_row.filepath):
                    os.remove(doc_row.filepath)
                
                # Delete from database (chunks will be deleted automatically due to CASCADE)
                conn.execute(text("DELETE FROM documents WHERE id = :id"), {"id": document_id})
            
            return {
                "success": True,
                "document_id": document_id
            }
            
        except Exception as e:
            current_app.logger.error(f"Error deleting document {document_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "code": "DELETE_ERROR"
            }
    
    def _document_exists(self, checksum: str) -> bool:
        """Check if document with given checksum exists."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT EXISTS(SELECT 1 FROM documents WHERE checksum = :checksum)
                """), {"checksum": checksum}).fetchone()
                return result[0] if result else False
        except Exception:
            return False
    
    def _save_document_to_db(self, filename: str, content: str, embedding: str, 
                           filepath: str, checksum: str, chunks: List[Dict[str, Any]]) -> int:
        """Save document and its chunks to database and return the document ID."""
        with self.engine.begin() as conn:
            # Save main document
            result = conn.execute(text("""
                INSERT INTO documents (filename, content, embedding, filepath, checksum) 
                VALUES (:filename, :content, :embedding, :filepath, :checksum)
                RETURNING id
            """), {
                "filename": filename,
                "content": content,
                "embedding": embedding,
                "filepath": filepath,
                "checksum": checksum
            })
            document_id = result.fetchone()[0]
            
            # Save chunks
            for chunk in chunks:
                chunk_embedding_str = self.embedding_service.format_embedding_for_db(chunk["embedding"])
                conn.execute(text("""
                    INSERT INTO document_chunks 
                    (document_id, chunk_index, content, embedding, token_count, start_char, end_char) 
                    VALUES (:document_id, :chunk_index, :content, :embedding, :token_count, :start_char, :end_char)
                """), {
                    "document_id": document_id,
                    "chunk_index": chunk["chunk_index"],
                    "content": chunk["text"],
                    "embedding": chunk_embedding_str,
                    "token_count": chunk["token_count"],
                    "start_char": chunk["start_char"],
                    "end_char": chunk["end_char"]
                })
            
            return document_id
