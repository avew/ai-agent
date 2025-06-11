"""
Embedding service for generating and managing vector embeddings.
"""
import openai
import tiktoken
from flask import current_app
from typing import List, Dict, Any


class EmbeddingService:
    """Service for handling text embeddings using OpenAI."""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=current_app.config['OPENAI_API_KEY'])
        self.model = current_app.config['EMBEDDING_MODEL']
        self.max_tokens = current_app.config.get('MAX_TOKENS_PER_CHUNK', 512)  # Max tokens per chunk
        self.chunk_overlap = current_app.config.get('CHUNK_OVERLAP_TOKENS', 50)  # Overlap between chunks
        self.encoding = tiktoken.encoding_for_model(current_app.config['EMBEDDING_MODEL'])  # Encoding for OpenAI models
    
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text string.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        return len(self.encoding.encode(text))
    
    def create_chunks(self, text: str) -> List[Dict[str, Any]]:
        """
        Split text into chunks based on token limits.
        
        Args:
            text: Text to split into chunks
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        # Split text into sentences first for better chunk boundaries
        sentences = self._split_into_sentences(text)
        chunks = []
        current_chunk = ""
        current_tokens = 0
        chunk_index = 0
        
        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)
            
            # If adding this sentence would exceed max tokens, finalize current chunk
            if current_tokens + sentence_tokens > self.max_tokens and current_chunk:
                chunks.append({
                    "text": current_chunk.strip(),
                    "chunk_index": chunk_index,
                    "token_count": current_tokens,
                    "start_char": len("".join([c["text"] for c in chunks])),
                    "end_char": len("".join([c["text"] for c in chunks])) + len(current_chunk)
                })
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk, self.chunk_overlap)
                current_chunk = overlap_text + " " + sentence if overlap_text else sentence
                current_tokens = self.count_tokens(current_chunk)
                chunk_index += 1
            else:
                # Add sentence to current chunk
                if current_chunk:
                    current_chunk += " " + sentence
                    current_tokens += sentence_tokens + 1  # +1 for space
                else:
                    current_chunk = sentence
                    current_tokens = sentence_tokens
        
        # Add final chunk if it has content
        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "chunk_index": chunk_index,
                "token_count": current_tokens,
                "start_char": len("".join([c["text"] for c in chunks[:-1]])) if chunks else 0,
                "end_char": len("".join([c["text"] for c in chunks[:-1]])) + len(current_chunk) if chunks else len(current_chunk)
            })
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences for better chunk boundaries.
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        import re
        
        # Simple sentence splitting on periods, exclamation marks, and question marks
        # followed by whitespace and a capital letter or end of string
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        
        # Filter out empty sentences and strip whitespace
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_overlap_text(self, text: str, overlap_tokens: int) -> str:
        """
        Get the last portion of text up to overlap_tokens for chunk overlap.
        
        Args:
            text: Text to get overlap from
            overlap_tokens: Number of tokens for overlap
            
        Returns:
            Overlap text
        """
        if overlap_tokens <= 0:
            return ""
        
        tokens = self.encoding.encode(text)
        if len(tokens) <= overlap_tokens:
            return text
        
        # Take the last overlap_tokens tokens
        overlap_token_ids = tokens[-overlap_tokens:]
        return self.encoding.decode(overlap_token_ids)
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for the given text.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            List of embedding values
            
        Raises:
            Exception: If embedding generation fails
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            current_app.logger.error(f"Error generating embedding: {e}")
            raise
    
    def get_embeddings_for_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for multiple text chunks.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            List of chunks with embeddings added
        """
        try:
            # Extract text from chunks for batch processing
            texts = [chunk["text"] for chunk in chunks]
            
            # Generate embeddings in batch for efficiency
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            
            # Add embeddings to chunks
            for i, chunk in enumerate(chunks):
                chunk["embedding"] = response.data[i].embedding
            
            return chunks
            
        except Exception as e:
            current_app.logger.error(f"Error generating embeddings for chunks: {e}")
            raise
    
    def format_embedding_for_db(self, embedding: List[float]) -> str:
        """
        Format embedding for PostgreSQL vector storage.
        
        Args:
            embedding: List of embedding values
            
        Returns:
            String formatted for PostgreSQL vector type
        """
        return "[" + ",".join(str(x) for x in embedding) + "]"
