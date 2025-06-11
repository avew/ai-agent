"""
Routes package initialization.
"""
from .documents import documents_bp
from .chat import chat_bp


def register_blueprints(app):
    """Register all blueprints with the Flask app."""
    app.register_blueprint(documents_bp)
    app.register_blueprint(chat_bp)
    
    # Health check endpoint at root level
    @app.route('/health')
    def health():
        return {"status": "healthy", "service": "chat-agent"}, 200
    
    # API info endpoint
    @app.route('/api')
    def api_info():
        return {
            "service": "Chat Agent API",
            "version": "1.0.0",
            "endpoints": {
                "documents": "/api/documents",
                "chat": "/api/chat",
                "health": "/health"
            }
        }, 200


__all__ = ['register_blueprints']
