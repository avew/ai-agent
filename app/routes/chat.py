"""
Chat routes for RAG (Retrieval Augmented Generation) functionality.
"""
from flask import Blueprint, request, jsonify, current_app

from ..services import SearchService
from ..utils import validate_chat_request

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')


@chat_bp.route('/', methods=['POST'])
def chat():
    """Process chat query using RAG."""
    try:
        data = request.get_json()
        
        # Validate request
        validation = validate_chat_request(data)
        if not validation['valid']:
            return jsonify({"error": validation['error']}), 400
        
        query = data['query']
        top_k = data.get('top_k', current_app.config['DEFAULT_TOP_K'])
        
        # Validate top_k if provided
        if not isinstance(top_k, int) or top_k < 1 or top_k > 20:
            return jsonify({"error": "top_k must be an integer between 1 and 20"}), 400
        
        # Process query
        search_service = SearchService()
        result = search_service.chat(query, top_k)
        
        if result['success']:
            return jsonify({
                "query": result['query'],
                "answer": result['answer'],
                "sources": result['sources'],
                "metadata": result['metadata']
            }), 200
        else:
            return jsonify({
                "error": "Failed to process query",
                "query": query,
                "answer": result.get('answer', 'Maaf, terjadi kesalahan.')
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Error in chat endpoint: {e}")
        return jsonify({
            "error": "Internal server error",
            "answer": "Maaf, terjadi kesalahan sistem. Silakan coba lagi."
        }), 500


@chat_bp.route('/search', methods=['POST'])
def search_documents():
    """Search documents without generating answer."""
    try:
        data = request.get_json()
        
        # Validate request
        validation = validate_chat_request(data)
        if not validation['valid']:
            return jsonify({"error": validation['error']}), 400
        
        query = data['query']
        top_k = data.get('top_k', current_app.config['DEFAULT_TOP_K'])
        
        # Validate top_k if provided
        if not isinstance(top_k, int) or top_k < 1 or top_k > 20:
            return jsonify({"error": "top_k must be an integer between 1 and 20"}), 400
        
        # Search documents
        search_service = SearchService()
        results = search_service.search_documents(query, top_k)
        
        return jsonify({
            "query": query,
            "results": [result.to_dict() for result in results],
            "count": len(results)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error in search endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500


@chat_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for chat service."""
    try:
        # Basic health check - verify OpenAI API key is configured
        if not current_app.config.get('OPENAI_API_KEY'):
            return jsonify({
                "status": "unhealthy",
                "error": "OpenAI API key not configured"
            }), 503
        
        return jsonify({
            "status": "healthy",
            "service": "chat",
            "embedding_model": current_app.config['EMBEDDING_MODEL'],
            "chat_model": current_app.config['CHAT_MODEL']
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error in health check: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 503
