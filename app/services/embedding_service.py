"""
Embedding service for generating and managing vector embeddings.
"""
import openai
from flask import current_app
from typing import List


class EmbeddingService:
    """Service for handling text embeddings using OpenAI."""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=current_app.config['OPENAI_API_KEY'])
        self.model = current_app.config['EMBEDDING_MODEL']
    
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
    
    def format_embedding_for_db(self, embedding: List[float]) -> str:
        """
        Format embedding for PostgreSQL vector storage.
        
        Args:
            embedding: List of embedding values
            
        Returns:
            String formatted for PostgreSQL vector type
        """
        return "[" + ",".join(str(x) for x in embedding) + "]"
