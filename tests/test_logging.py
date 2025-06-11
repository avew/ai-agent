#!/usr/bin/env python3
"""
Test script to demonstrate the new logging functionality for score tracking.
"""
import os
import sys
from dotenv import load_dotenv

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

# Load environment variables
load_dotenv()

from app import create_app
from app.services.search_service import SearchService

def test_logging():
    """Test the logging functionality with a sample query."""
    print("🧪 Testing Score Logging Functionality")
    print("=" * 50)
    
    # Create Flask app
    app = create_app('development')
    
    with app.app_context():
        try:
            # Initialize search service
            search_service = SearchService()
            
            # Test query
            test_query = "artificial intelligence"
            
            print(f"📝 Testing with query: '{test_query}'")
            print("📊 Check the logs for detailed score information...")
            print()
            
            # Perform search (this will generate logs)
            result = search_service.chat(test_query, top_k=3)
            
            print("✅ Test completed successfully!")
            print(f"📋 Query: {result['query']}")
            print(f"🎯 Success: {result['success']}")
            print(f"📈 Relevance Score: {result['metadata']['relevance_score']:.4f}")
            print(f"📚 Sources Used: {result['metadata']['sources_used']}")
            print(f"🤖 Model Used: {result['metadata']['model_used']}")
            print()
            print("📝 Check the console output and log file (if enabled) for detailed score breakdowns!")
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            print("💡 Make sure your database is set up and contains some documents.")

if __name__ == "__main__":
    test_logging()
