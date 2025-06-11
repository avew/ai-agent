"""
Entry point for the Chat Agent Flask application.
"""
import os
from app import create_app

# Create Flask application
app = create_app()

if __name__ == "__main__":
    # Configuration for development
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"🚀 Starting Chat Agent on http://{host}:{port}")
    print(f"📝 Debug mode: {'enabled' if debug else 'disabled'}")
    print(f"📁 Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"🤖 Embedding model: {app.config['EMBEDDING_MODEL']}")
    print(f"🤖 Max token per chunk: {app.config['MAX_TOKENS_PER_CHUNK']}")
    print(f"🤖 Chunk Overlap: {app.config['CHUNK_OVERLAP_TOKENS']}")
    print(f"💬 Chat model: {app.config['CHAT_MODEL']}")
    
    app.run(host=host, port=port, debug=debug)
