"""
Document routes for file upload, download, and management.
"""
import os
from flask import Blueprint, request, jsonify, send_file, current_app

from ..services import DocumentService
from ..utils import validate_file_upload, validate_pagination_params

documents_bp = Blueprint('documents', __name__, url_prefix='/api/documents')


@documents_bp.route('/upload', methods=['POST'])
def upload_document():
    """Upload a new document."""
    # Validate file
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    validation = validate_file_upload(file)
    
    if not validation['valid']:
        return jsonify({"error": validation['error']}), 400
    
    # Process upload
    document_service = DocumentService()
    result = document_service.upload_document(file, file.filename)
    
    if result['success']:
        return jsonify({
            "message": "Document uploaded successfully",
            "document_id": result['document_id'],
            "filename": result['filename'],
            "checksum": result['checksum']
        }), 201
    else:
        status_code = 409 if result.get('code') == 'DUPLICATE' else 400
        return jsonify({"error": result['error']}), status_code


@documents_bp.route('/', methods=['GET'])
def list_documents():
    """Get paginated list of documents."""
    page = request.args.get('page', '1')
    per_page = request.args.get('per_page', '10')
    
    # Validate pagination
    validation = validate_pagination_params(page, per_page)
    if not validation['valid']:
        return jsonify({"error": validation['error']}), 400
    
    # Get documents
    document_service = DocumentService()
    result = document_service.get_documents(
        page=validation['page'],
        per_page=validation['per_page']
    )
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify({"error": result['error']}), 500


@documents_bp.route('/<int:document_id>', methods=['GET'])
def get_document(document_id):
    """Get document details by ID."""
    document_service = DocumentService()
    document = document_service.get_document_by_id(document_id)
    
    if document:
        return jsonify({
            "document": {
                "id": document.id,
                "filename": document.filename,
                "checksum": document.checksum,
                "created_at": document.created_at.isoformat() if document.created_at else None,
                "updated_at": document.updated_at.isoformat() if document.updated_at else None,
                "download_url": f"/api/documents/{document.id}/download"
            }
        }), 200
    else:
        return jsonify({"error": "Document not found"}), 404


@documents_bp.route('/<int:document_id>/download', methods=['GET'])
def download_document(document_id):
    """Download document file."""
    document_service = DocumentService()
    document = document_service.get_document_by_id(document_id)
    
    if not document:
        return jsonify({"error": "Document not found"}), 404
    
    if not os.path.exists(document.filepath):
        return jsonify({"error": "File not found on server"}), 404
    
    try:
        return send_file(
            document.filepath,
            as_attachment=True,
            download_name=document.filename
        )
    except Exception as e:
        current_app.logger.error(f"Error downloading file: {e}")
        return jsonify({"error": "Error downloading file"}), 500


@documents_bp.route('/<int:document_id>', methods=['DELETE'])
def delete_document(document_id):
    """Delete document by ID."""
    document_service = DocumentService()
    result = document_service.delete_document(document_id)
    
    if result['success']:
        return jsonify({
            "message": "Document deleted successfully",
            "document_id": result['document_id']
        }), 200
    else:
        status_code = 404 if result.get('code') == 'NOT_FOUND' else 500
        return jsonify({"error": result['error']}), status_code


@documents_bp.route('/stats', methods=['GET'])
def get_document_stats():
    """Get document statistics."""
    try:
        document_service = DocumentService()
        # Get basic stats from first page
        result = document_service.get_documents(page=1, per_page=1)
        
        if result['success']:
            return jsonify({
                "total_documents": result['pagination']['total'],
                "upload_folder": current_app.config['UPLOAD_FOLDER']
            }), 200
        else:
            return jsonify({"error": "Error getting statistics"}), 500
            
    except Exception as e:
        current_app.logger.error(f"Error getting stats: {e}")
        return jsonify({"error": "Error getting statistics"}), 500
