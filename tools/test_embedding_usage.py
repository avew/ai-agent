#!/usr/bin/env python3
"""
Test script untuk demonstrasi embedding usage logging.
"""
import os
import sys
from dotenv import load_dotenv

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app import create_app

def test_embedding_logging():
    """Test embedding usage logging dengan sample data."""
    print("🧪 TESTING EMBEDDING USAGE LOGGING")
    print("=" * 60)
    
    # Create Flask app
    app = create_app('development')
    
    with app.app_context():
        try:
            from app.services.embedding_service import EmbeddingService
            
            # Initialize embedding service
            embedding_service = EmbeddingService()
            
            print(f"✅ Embedding Service initialized")
            print(f"🤖 Model: {embedding_service.model}")
            print(f"💰 Pricing: ${embedding_service.embedding_pricing.get(embedding_service.model, 0.0001):.6f} per 1K tokens")
            print()
            
            # Test 1: Single text embedding
            print("📝 Test 1: Single text embedding")
            test_text = "This is a test text for embedding generation to demonstrate cost tracking."
            token_count = embedding_service.count_tokens(test_text)
            print(f"   Text: '{test_text}'")
            print(f"   Tokens: {token_count}")
            
            embedding = embedding_service.get_embedding(test_text)
            print(f"   ✅ Embedding generated: {len(embedding)} dimensions")
            print()
            
            # Test 2: Multiple chunks embedding
            print("📝 Test 2: Multiple chunks embedding")
            sample_chunks = [
                {
                    "text": "Artificial Intelligence (AI) is transforming various industries with its capabilities.",
                    "chunk_index": 0,
                    "token_count": 0,
                    "start_char": 0,
                    "end_char": 0
                },
                {
                    "text": "Machine Learning is a subset of AI that enables systems to learn from data.",
                    "chunk_index": 1,
                    "token_count": 0,
                    "start_char": 0,
                    "end_char": 0
                },
                {
                    "text": "Deep Learning uses neural networks to process complex patterns in data.",
                    "chunk_index": 2,
                    "token_count": 0,
                    "start_char": 0,
                    "end_char": 0
                },
                {
                    "text": "Natural Language Processing enables computers to understand human language.",
                    "chunk_index": 3,
                    "token_count": 0,
                    "start_char": 0,
                    "end_char": 0
                },
                {
                    "text": "Computer Vision allows machines to interpret and understand visual information.",
                    "chunk_index": 4,
                    "token_count": 0,
                    "start_char": 0,
                    "end_char": 0
                }
            ]
            
            # Update token counts
            for chunk in sample_chunks:
                chunk["token_count"] = embedding_service.count_tokens(chunk["text"])
            
            total_tokens = sum(chunk["token_count"] for chunk in sample_chunks)
            print(f"   Chunks: {len(sample_chunks)}")
            print(f"   Total tokens: {total_tokens}")
            
            # Generate embeddings
            chunks_with_embeddings = embedding_service.get_embeddings_for_chunks(sample_chunks)
            print(f"   ✅ Embeddings generated for {len(chunks_with_embeddings)} chunks")
            print()
            
            # Test 3: Chunking and embedding a longer text
            print("📝 Test 3: Text chunking and embedding")
            long_text = """
            Large Language Models (LLMs) represent a significant advancement in artificial intelligence and natural language processing. 
            These models, such as GPT-4, BERT, and others, are trained on vast amounts of text data and can perform a wide variety 
            of language-related tasks. The development of LLMs has revolutionized many applications including chatbots, content generation, 
            translation, summarization, and question-answering systems. The architecture of these models is typically based on the 
            Transformer architecture, which uses attention mechanisms to process and understand contextual relationships in text. 
            Training these models requires substantial computational resources and large datasets, but the results have been remarkable 
            in terms of their ability to understand and generate human-like text. The applications of LLMs continue to expand across 
            various industries including healthcare, finance, education, and technology.
            """
            
            # Create chunks
            chunks = embedding_service.create_chunks(long_text.strip())
            print(f"   Original text length: {len(long_text.strip())} characters")
            print(f"   Created chunks: {len(chunks)}")
            
            total_chunk_tokens = sum(chunk["token_count"] for chunk in chunks)
            print(f"   Total tokens in chunks: {total_chunk_tokens}")
            
            # Generate embeddings for chunks
            chunks_with_embeddings = embedding_service.get_embeddings_for_chunks(chunks)
            print(f"   ✅ Embeddings generated for all chunks")
            print()
            
            print("🎉 Test completed successfully!")
            print("📊 Check the logs for detailed cost tracking information.")
            print("💡 Use the following commands to analyze usage:")
            print("   python analyze_embedding_usage.py --days 1")
            print("   python monitor_embedding_usage.py")
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_embedding_logging()
