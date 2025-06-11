"""
Search service for RAG (Retrieval Augmented Generation) functionality.
"""
import openai
from flask import current_app
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from typing import List, Dict, Any

from ..models import SearchResult
from .embedding_service import EmbeddingService


class SearchService:
    """Service for handling document search and RAG operations."""
    
    def __init__(self):
        self.engine = create_engine(current_app.config['DATABASE_URL'], poolclass=NullPool)
        self.embedding_service = EmbeddingService()
        self.client = openai.OpenAI(api_key=current_app.config['OPENAI_API_KEY'])
        self.chat_model = current_app.config['CHAT_MODEL']
        self.max_context_length = current_app.config['MAX_CONTEXT_LENGTH']
        self.default_top_k = current_app.config['DEFAULT_TOP_K']
    
    def search_documents(self, query: str, top_k: int = None) -> List[SearchResult]:
        """
        Search for relevant documents using vector similarity.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of search results
        """
        if top_k is None:
            top_k = self.default_top_k
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.get_embedding(query)
            embedding_str = self.embedding_service.format_embedding_for_db(query_embedding)
            
            # Search for similar documents using cosine distance
            with self.engine.connect() as conn:
                rows = conn.execute(text("""
                    SELECT id, filename, content, (embedding <=> :query_embedding) AS distance
                    FROM documents
                    ORDER BY distance ASC
                    LIMIT :top_k
                """), {
                    "query_embedding": embedding_str,
                    "top_k": top_k
                }).fetchall()
            
            results = []
            for row in rows:
                results.append(SearchResult(
                    content=row.content,
                    filename=row.filename,
                    distance=row.distance
                ))
            
            return results
            
        except Exception as e:
            current_app.logger.error(f"Error searching documents: {e}")
            return []
    
    def generate_answer(self, query: str, contexts: List[SearchResult]) -> Dict[str, Any]:
        """
        Generate answer using RAG approach.
        
        Args:
            query: User question
            contexts: Relevant document contexts
            
        Returns:
            Dictionary with generated answer and metadata
        """
        try:
            # Prepare context text
            context_texts = []
            for context in contexts:
                # Truncate content to prevent token limit issues
                truncated_content = context.content[:self.max_context_length]
                context_texts.append(f"[{context.filename}]\n{truncated_content}")
            
            context_str = "\n\n---\n\n".join(context_texts)
            
            # Create prompt
            system_prompt = """Kamu adalah asisten AI yang membantu menjawab pertanyaan berdasarkan knowledge base yang diberikan. 
Gunakan informasi dari konteks yang relevan untuk memberikan jawaban yang akurat dan informatif. 
Jika informasi tidak tersedia dalam konteks, sampaikan bahwa informasi tersebut tidak ada dalam knowledge base."""
            
            user_prompt = f"""Konteks dari knowledge base:
{context_str}

Pertanyaan: {query}

Berikan jawaban yang jelas dan akurat berdasarkan konteks di atas."""
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Calculate relevance score (average of inverse distances)
            if contexts:
                relevance_score = sum(1 / (1 + context.distance) for context in contexts) / len(contexts)
            else:
                relevance_score = 0.0
            
            return {
                "success": True,
                "answer": answer,
                "relevance_score": relevance_score,
                "sources_used": len(contexts),
                "model_used": self.chat_model
            }
            
        except Exception as e:
            current_app.logger.error(f"Error generating answer: {e}")
            return {
                "success": False,
                "error": str(e),
                "answer": "Maaf, terjadi kesalahan saat memproses pertanyaan Anda."
            }
    
    def chat(self, query: str, top_k: int = None) -> Dict[str, Any]:
        """
        Complete RAG pipeline: search + generate answer.
        
        Args:
            query: User question
            top_k: Number of documents to retrieve
            
        Returns:
            Dictionary with answer and metadata
        """
        # Search for relevant documents
        search_results = self.search_documents(query, top_k)
        
        # Generate answer
        answer_result = self.generate_answer(query, search_results)
        
        # Combine results
        return {
            "query": query,
            "answer": answer_result.get("answer", ""),
            "success": answer_result.get("success", False),
            "sources": [result.to_dict() for result in search_results],
            "metadata": {
                "relevance_score": answer_result.get("relevance_score", 0.0),
                "sources_used": answer_result.get("sources_used", 0),
                "model_used": answer_result.get("model_used", ""),
                "top_k": top_k or self.default_top_k
            }
        }
