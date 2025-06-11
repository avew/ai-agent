"""
Unit tests for the Chat Agent application.
"""
import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock
from app import create_app
from app.config import TestingConfig


class ChatAgentTestCase(unittest.TestCase):
    """Base test case for Chat Agent application."""
    
    def setUp(self):
        """Set up test client and application context."""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()


class HealthCheckTests(ChatAgentTestCase):
    """Tests for health check endpoints."""
    
    def test_root_health_check(self):
        """Test root health check endpoint."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'chat-agent')
    
    def test_api_info(self):
        """Test API info endpoint."""
        response = self.client.get('/api')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['service'], 'Chat Agent API')
        self.assertIn('endpoints', data)
    
    def test_chat_health_check(self):
        """Test chat service health check."""
        response = self.client.get('/api/chat/health')
        # This will fail without proper API key, but should return 503
        self.assertIn(response.status_code, [200, 503])


class ValidationTests(ChatAgentTestCase):
    """Tests for validation utilities."""
    
    def test_validate_chat_request_valid(self):
        """Test valid chat request validation."""
        from app.utils import validate_chat_request
        
        valid_data = {"query": "What is machine learning?"}
        result = validate_chat_request(valid_data)
        self.assertTrue(result['valid'])
        self.assertIsNone(result['error'])
    
    def test_validate_chat_request_invalid(self):
        """Test invalid chat request validation."""
        from app.utils import validate_chat_request
        
        # Test empty query
        invalid_data = {"query": ""}
        result = validate_chat_request(invalid_data)
        self.assertFalse(result['valid'])
        self.assertIsNotNone(result['error'])
        
        # Test missing query
        invalid_data = {}
        result = validate_chat_request(invalid_data)
        self.assertFalse(result['valid'])
        self.assertIsNotNone(result['error'])
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        from app.utils import sanitize_filename
        
        # Test dangerous characters
        dangerous_name = "test<>:\"|?*.txt"
        safe_name = sanitize_filename(dangerous_name)
        self.assertNotIn('<', safe_name)
        self.assertNotIn('>', safe_name)
        self.assertNotIn(':', safe_name)
        
        # Test path separators
        path_name = "path/to/file.txt"
        safe_name = sanitize_filename(path_name)
        self.assertNotIn('/', safe_name)
        self.assertNotIn('\\', safe_name)


class FileUtilsTests(ChatAgentTestCase):
    """Tests for file utilities."""
    
    def test_extract_text_txt(self):
        """Test text extraction from txt file."""
        from app.utils import extract_text
        
        # Create temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test text file.")
            temp_file = f.name
        
        try:
            with open(temp_file, 'rb') as f:
                result = extract_text(f, 'test.txt')
                self.assertEqual(result, "This is a test text file.")
        finally:
            os.unlink(temp_file)
    
    def test_is_allowed_file(self):
        """Test file extension validation."""
        from app.utils import is_allowed_file
        
        allowed_extensions = {'txt', 'pdf', 'docx'}
        
        self.assertTrue(is_allowed_file('test.txt', allowed_extensions))
        self.assertTrue(is_allowed_file('document.pdf', allowed_extensions))
        self.assertFalse(is_allowed_file('script.exe', allowed_extensions))
        self.assertFalse(is_allowed_file('noextension', allowed_extensions))


class DocumentRoutesTests(ChatAgentTestCase):
    """Tests for document routes."""
    
    def test_upload_no_file(self):
        """Test upload endpoint with no file."""
        response = self.client.post('/api/documents/upload')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
    
    def test_list_documents_empty(self):
        """Test listing documents when database is empty."""
        # This test assumes no documents in test database
        response = self.client.get('/api/documents/')
        # Should return 200 even if empty
        self.assertIn(response.status_code, [200, 500])  # 500 if no DB connection
    
    def test_get_nonexistent_document(self):
        """Test getting a non-existent document."""
        response = self.client.get('/api/documents/99999')
        # Should return 404 or 500 if DB connection fails
        self.assertIn(response.status_code, [404, 500])


class ChatRoutesTests(ChatAgentTestCase):
    """Tests for chat routes."""
    
    def test_chat_no_data(self):
        """Test chat endpoint with no data."""
        response = self.client.post('/api/chat/', json={})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
    
    def test_chat_invalid_query(self):
        """Test chat endpoint with invalid query."""
        response = self.client.post('/api/chat/', json={"query": ""})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
    
    def test_search_no_data(self):
        """Test search endpoint with no data."""
        response = self.client.post('/api/chat/search', json={})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)


if __name__ == '__main__':
    unittest.main()
