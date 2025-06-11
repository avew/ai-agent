"""
Search service for RAG (Retrieval Augmented Generation) functionality.
"""
import openai
from flask import current_app
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from typing import List, Dict, Any

from ..models import SearchResult, DocumentChunk
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
        self.system_prompt = current_app.config['SYSTEM_PROMPT']
        self.user_prompt_template = current_app.config['USER_PROMPT_TEMPLATE']
    
    def search_documents(self, query: str, top_k: int = None) -> List[SearchResult]:
        """
        Search for relevant document chunks using vector similarity.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of search results from document chunks
        """
        if top_k is None:
            top_k = self.default_top_k
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.get_embedding(query)
            embedding_str = self.embedding_service.format_embedding_for_db(query_embedding)
            
            current_app.logger.info(f"Search Query: '{query}' | Top K: {top_k}")
            
            # Search for similar document chunks using cosine distance
            with self.engine.connect() as conn:
                rows = conn.execute(text("""
                    SELECT 
                        dc.content,
                        d.filename,
                        dc.chunk_index,
                        dc.token_count,
                        dc.start_char,
                        dc.end_char,
                        (dc.embedding <=> :query_embedding) AS distance
                    FROM document_chunks dc
                    JOIN documents d ON dc.document_id = d.id
                    ORDER BY distance ASC
                """), {
                    "query_embedding": embedding_str
                }).fetchmany(top_k)
            
            results = []
            distances = []
            
            for i, row in enumerate(rows):
                # Convert distance to similarity score (1 - distance for cosine distance)
                similarity_score = 1 - row.distance
                distances.append(row.distance)
                
                # Enhanced search result with chunk information
                results.append(SearchResult(
                    content=row.content,
                    filename=f"{row.filename} (chunk {row.chunk_index + 1})",
                    distance=row.distance,
                    chunk_index=row.chunk_index
                ))
                
                # Log individual result scores
                current_app.logger.debug(f"Result {i+1}: {row.filename} (chunk {row.chunk_index + 1}) | "
                                       f"Distance: {row.distance:.4f} | Similarity: {similarity_score:.4f}")
            
            # Log summary statistics
            if distances:
                avg_distance = sum(distances) / len(distances)
                min_distance = min(distances)
                max_distance = max(distances)
                avg_similarity = 1 - avg_distance
                
                current_app.logger.info(f"Search Results Summary - Found: {len(results)} | "
                                       f"Avg Distance: {avg_distance:.4f} | "
                                       f"Avg Similarity: {avg_similarity:.4f} | "
                                       f"Best Match Distance: {min_distance:.4f} | "
                                       f"Worst Match Distance: {max_distance:.4f}")
            else:
                current_app.logger.warning(f"No search results found for query: '{query}'")
            
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
            
            # Create prompt using configurable system prompt
            system_prompt = self.system_prompt
            
            # Create user prompt using configurable template
            user_prompt = self.user_prompt_template.format(
                context=context_str,
                query=query
            )
            
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
                
                # Log relevance score details
                individual_scores = [1 / (1 + context.distance) for context in contexts]
                current_app.logger.info(f"Relevance Score Calculation - "
                                       f"Overall Score: {relevance_score:.4f} | "
                                       f"Individual Scores: {[f'{score:.4f}' for score in individual_scores]} | "
                                       f"Sources Used: {len(contexts)}")
            else:
                relevance_score = 0.0
                current_app.logger.warning("No contexts available for relevance score calculation")
            
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
        current_app.logger.info(f"RAG Chat Pipeline Started - Query: '{query}' | Top K: {top_k or self.default_top_k}")
        
        # Search for relevant documents
        search_results = self.search_documents(query, top_k)
        
        # Analyze search quality
        quality_metrics = self.analyze_search_quality(search_results)
        
        # Generate answer
        answer_result = self.generate_answer(query, search_results)
        
        # Log final results
        final_relevance_score = answer_result.get("relevance_score", 0.0)
        success = answer_result.get("success", False)
        
        current_app.logger.info(f"RAG Chat Pipeline Completed - "
                               f"Success: {success} | "
                               f"Final Relevance Score: {final_relevance_score:.4f} | "
                               f"Sources Found: {len(search_results)} | "
                               f"Model Used: {answer_result.get('model_used', 'N/A')}")
        
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
    
    def analyze_search_quality(self, search_results: List[SearchResult]) -> Dict[str, Any]:
        """
        Analyze the quality of search results and provide detailed metrics.
        
        Args:
            search_results: List of search results to analyze
            
        Returns:
            Dictionary with detailed quality metrics
        """
        if not search_results:
            return {
                "total_results": 0,
                "quality_assessment": "No results found"
            }
        
        distances = [result.distance for result in search_results]
        similarities = [1 - distance for distance in distances]
        
        # Calculate various metrics
        metrics = {
            "total_results": len(search_results),
            "distances": {
                "min": min(distances),
                "max": max(distances),
                "avg": sum(distances) / len(distances),
                "std": self._calculate_std(distances)
            },
            "similarities": {
                "min": min(similarities),
                "max": max(similarities),
                "avg": sum(similarities) / len(similarities),
                "std": self._calculate_std(similarities)
            }
        }
        
        # Quality assessment based on similarity scores
        avg_similarity = metrics["similarities"]["avg"]
        if avg_similarity >= 0.8:
            quality = "Excellent"
        elif avg_similarity >= 0.6:
            quality = "Good"
        elif avg_similarity >= 0.4:
            quality = "Fair"
        else:
            quality = "Poor"
        
        metrics["quality_assessment"] = quality
        
        # Log detailed analysis
        current_app.logger.info(f"Search Quality Analysis - "
                               f"Quality: {quality} | "
                               f"Avg Similarity: {avg_similarity:.4f} | "
                               f"Best Match: {max(similarities):.4f} | "
                               f"Worst Match: {min(similarities):.4f}")
        
        return metrics
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation of a list of values."""
        if len(values) <= 1:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
