#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def test_log_entry():
    """Test adding a manual log entry."""
    from app import create_app
    
    print("🧪 TESTING LOG ENTRY")
    print("=" * 50)
    
    app = create_app('development')
    
    with app.app_context():
        # Manually log an embedding usage entry
        app.logger.info(
            "EMBEDDING_USAGE | Operation: test_manual | "
            "Model: text-embedding-3-small | "
            "Tokens: 123 | "
            "Requests: 1 | "
            "Time: 0.456s | "
            "Cost: $0.000003 USD"
        )
        print("✅ Manual log entry added")
        print("📊 Check logs/app.log for the entry")

if __name__ == "__main__":
    test_log_entry()
