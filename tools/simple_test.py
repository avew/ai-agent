#!/usr/bin/env python3
"""
Simple test untuk embedding service.
"""
import os
import sys
from dotenv import load_dotenv

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

# Load environment variables
load_dotenv()

from app import create_app

def simple_test():
    """Simple test untuk embedding service."""
    print("🧪 SIMPLE EMBEDDING TEST")
    print("=" * 50)
    
    # Create Flask app
    app = create_app('development')
    
    with app.app_context():
        try:
            from app.services.embedding_service import EmbeddingService
            
            # Initialize embedding service
            service = EmbeddingService()
            
            print("✅ Service initialized")
            print(f"🤖 Model: {service.model}")
            print(f"💰 Pricing: {service.embedding_pricing}")
            print()
            
            # Test token counting
            test_text = "Hello world, this is a test for embedding cost tracking"
            tokens = service.count_tokens(test_text)
            cost = service.calculate_embedding_cost(tokens)
            
            print(f"📝 Test text: '{test_text}'")
            print(f"🎯 Tokens: {tokens}")
            print(f"💰 Estimated cost: ${cost:.8f}")
            print()
            
            # Test logging (without actual API call)
            service.log_embedding_usage(
                operation="test",
                token_count=tokens,
                request_count=1,
                processing_time=0.123,
                cost=cost
            )
            
            print("✅ Logging test completed")
            print("📊 Check logs/app.log for the embedding usage entry")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    simple_test()
