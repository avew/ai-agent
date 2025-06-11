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
        self.max_tokens = current_app.config.get('MAX_TOKENS_PER_CHUNK', 512)
        self.chunk_overlap = current_app.config.get('CHUNK_OVERLAP_TOKENS', 50)
        self.encoding = tiktoken.encoding_for_model(self.model)

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text string."""
        return len(self.encoding.encode(text))

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
        Generate embeddings for multiple text chunks (with batching).
        Embeddings are added in-place as key 'embedding'.
        """
        BATCH_SIZE = 100  # OpenAI Embedding API batch limit

        texts = [chunk["text"] for chunk in chunks]
        embeddings = []
        try:
            for i in range(0, len(texts), BATCH_SIZE):
                batch_texts = texts[i:i+BATCH_SIZE]
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch_texts
                )
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
            assert len(embeddings) == len(chunks)
            for i, chunk in enumerate(chunks):
                chunk["embedding"] = embeddings[i]
            return chunks
        except Exception as e:
            current_app.logger.error(f"Error generating embeddings for chunks: {e}")
            raise

    def format_embedding_for_db(self, embedding: List[float]) -> str:
        """
        Format embedding for PostgreSQL vector storage.
        """
        return "[" + ",".join(f"{x:.8g}" for x in embedding) + "]"
