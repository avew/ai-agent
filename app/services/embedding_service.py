"""
Embedding service for generating and managing vector embeddings.
"""
import openai
import tiktoken
import time
from flask import current_app
from typing import List, Dict, Any


class EmbeddingService:
    """Service for handling text embeddings using OpenAI."""

    def __init__(self):
        self.client = openai.OpenAI(api_key=current_app.config['OPENAI_API_KEY'])
        self.model = current_app.config['EMBEDDING_MODEL']
        self.max_tokens = current_app.config.get('MAX_TOKENS_PER_CHUNK', 512)
        self.chunk_overlap = current_app.config.get('CHUNK_OVERLAP_TOKENS', 50)
        self.encoding = tiktoken.encoding_for_model(self.model)
        
        # Pricing per 1K tokens (update these based on current OpenAI pricing)
        self.embedding_pricing = {
            'text-embedding-3-small': 0.00002,  # $0.00002 per 1K tokens
            'text-embedding-3-large': 0.00013,  # $0.00013 per 1K tokens
            'text-embedding-ada-002': 0.0001,   # $0.0001 per 1K tokens
        }

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text string."""
        return len(self.encoding.encode(text))

    def calculate_embedding_cost(self, total_tokens: int) -> float:
        """
        Calculate the cost of embedding based on token count and model pricing.
        
        Args:
            total_tokens: Total number of tokens processed
            
        Returns:
            Cost in USD
        """
        price_per_1k_tokens = self.embedding_pricing.get(self.model, 0.0001)  # Default fallback
        return (total_tokens / 1000.0) * price_per_1k_tokens
    
    def log_embedding_usage(self, operation: str, token_count: int, request_count: int, 
                           processing_time: float, cost: float):
        """
        Log embedding API usage for cost tracking.
        
        Args:
            operation: Type of operation (e.g., 'single_text', 'batch_chunks')
            token_count: Number of tokens processed
            request_count: Number of API requests made
            processing_time: Time taken for processing (seconds)
            cost: Estimated cost in USD
        """
        current_app.logger.info(
            f"EMBEDDING_USAGE | Operation: {operation} | "
            f"Model: {self.model} | "
            f"Tokens: {token_count:,} | "
            f"Requests: {request_count} | "
            f"Time: {processing_time:.3f}s | "
            f"Cost: ${cost:.6f} USD"
        )

    def create_chunks(self, text: str) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks based on token limits.
        Returns:
            List of chunk dicts: {text, chunk_index, token_count, start_char, end_char}
        """
        tokens = self.encoding.encode(text)
        n_tokens = len(tokens)
        chunks = []
        start = 0
        chunk_index = 0

        while start < n_tokens:
            end = min(start + self.max_tokens, n_tokens)
            chunk_token_ids = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_token_ids)
            chunk_token_count = len(chunk_token_ids)

            # Char indices (approximate, may not match perfectly for complex encodings)
            char_start = len(self.encoding.decode(tokens[:start]))
            char_end = char_start + len(chunk_text)

            chunks.append({
                "text": chunk_text.strip(),
                "chunk_index": chunk_index,
                "token_count": chunk_token_count,
                "start_char": char_start,
                "end_char": char_end,
            })
            chunk_index += 1

            # Geser window dengan overlap
            if end == n_tokens:
                break
            start += self.max_tokens - self.chunk_overlap

        return chunks

    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text string.
        """
        start_time = time.time()
        token_count = self.count_tokens(text)
        
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            
            processing_time = time.time() - start_time
            cost = self.calculate_embedding_cost(token_count)
            
            # Log usage
            self.log_embedding_usage(
                operation="single_text",
                token_count=token_count,
                request_count=1,
                processing_time=processing_time,
                cost=cost
            )
            
            return response.data[0].embedding
        except Exception as e:
            processing_time = time.time() - start_time
            current_app.logger.error(
                f"Error generating embedding: {e} | "
                f"Tokens: {token_count} | Time: {processing_time:.3f}s"
            )
            raise

    def get_embeddings_for_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for multiple text chunks (with batching).
        Embeddings are added in-place as key 'embedding'.
        """
        BATCH_SIZE = 100  # OpenAI Embedding API batch limit
        
        start_time = time.time()
        texts = [chunk["text"] for chunk in chunks]
        total_tokens = sum(self.count_tokens(text) for text in texts)
        total_requests = 0
        
        embeddings = []
        try:
            for i in range(0, len(texts), BATCH_SIZE):
                batch_start_time = time.time()
                batch_texts = texts[i:i+BATCH_SIZE]
                batch_tokens = sum(self.count_tokens(text) for text in batch_texts)
                
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch_texts
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
                total_requests += 1
                
                batch_time = time.time() - batch_start_time
                batch_cost = self.calculate_embedding_cost(batch_tokens)
                
                # Log each batch
                current_app.logger.debug(
                    f"EMBEDDING_BATCH | Batch {total_requests}/{(len(texts) + BATCH_SIZE - 1) // BATCH_SIZE} | "
                    f"Texts: {len(batch_texts)} | "
                    f"Tokens: {batch_tokens:,} | "
                    f"Time: {batch_time:.3f}s | "
                    f"Cost: ${batch_cost:.6f}"
                )
            
            assert len(embeddings) == len(chunks)
            for i, chunk in enumerate(chunks):
                chunk["embedding"] = embeddings[i]
            
            # Log total usage
            total_time = time.time() - start_time
            total_cost = self.calculate_embedding_cost(total_tokens)
            
            self.log_embedding_usage(
                operation="batch_chunks",
                token_count=total_tokens,
                request_count=total_requests,
                processing_time=total_time,
                cost=total_cost
            )
            
            return chunks
        except Exception as e:
            total_time = time.time() - start_time
            current_app.logger.error(
                f"Error generating embeddings for chunks: {e} | "
                f"Total tokens: {total_tokens:,} | "
                f"Requests made: {total_requests} | "
                f"Time: {total_time:.3f}s"
            )
            raise

    def format_embedding_for_db(self, embedding: List[float]) -> str:
        """
        Format embedding for PostgreSQL vector storage.
        """
        return "[" + ",".join(f"{x:.8g}" for x in embedding) + "]"
