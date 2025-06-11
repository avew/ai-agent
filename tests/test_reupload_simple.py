"""
Simple integration test for the reupload functionality.
"""
import unittest
import tempfile
import os
import json
from app import create_app


class SimpleReuploadTest(unittest.TestCase):
    """Simple test for reupload endpoint validation."""
    
    def setUp(self):
        """Set up test client."""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()
    
    def test_reupload_no_file(self):
        """Test reupload without file returns 400."""
        response = self.client.put('/api/documents/1/reupload')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data['error'], 'No file uploaded')
    
    def test_reupload_invalid_file_type(self):
        """Test reupload with invalid file type."""
        # Create a test file with invalid extension
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.exe') as f:
            f.write("Invalid content")
            temp_file = f.name
        
        try:
            with open(temp_file, 'rb') as file:
                data = {
                    'file': (file, 'virus.exe', 'application/exe')
                }
                response = self.client.put('/api/documents/1/reupload', 
                                         data=data, 
                                         content_type='multipart/form-data')
            
            # Should return 400 for invalid file type
            self.assertEqual(response.status_code, 400)
            
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_reupload_route_exists(self):
        """Test that the reupload route is properly registered."""
        # This test verifies the route exists by checking it doesn't return 404
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Test content")
            temp_file = f.name
        
        try:
            with open(temp_file, 'rb') as file:
                data = {
                    'file': (file, 'test.txt', 'text/plain')
                }
                response = self.client.put('/api/documents/1/reupload', 
                                         data=data, 
                                         content_type='multipart/form-data')
            
            # Should not return 404 (route not found)
            self.assertNotEqual(response.status_code, 404)
            
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)


if __name__ == '__main__':
    unittest.main()
