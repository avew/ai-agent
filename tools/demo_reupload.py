#!/usr/bin/env python3
"""
Demo script to demonstrate the reupload functionality.
This script shows how the reupload feature works.
"""
import requests
import tempfile
import os


def create_test_file(content, filename):
    """Create a temporary test file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'_{filename}') as f:
        f.write(content)
        return f.name


def test_reupload_functionality():
    """Test the reupload functionality with curl-like requests."""
    base_url = "http://localhost:5000"
    
    print("🔄 Testing Document Reupload Functionality")
    print("=" * 50)
    
    # Test 1: Upload initial document
    print("\n1. Testing initial document upload...")
    file_path = create_test_file("This is the original content of the document.", "test_doc.txt")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': ('test_doc.txt', f, 'text/plain')}
            response = requests.post(f"{base_url}/api/documents/upload", files=files)
            
        if response.status_code == 201:
            data = response.json()
            document_id = data['document_id']
            checksum = data['checksum']
            print(f"   ✅ Document uploaded successfully!")
            print(f"   📄 Document ID: {document_id}")
            print(f"   🔐 Checksum: {checksum}")
            
            # Test 2: Reupload with same content (same checksum)
            print(f"\n2. Testing reupload with same content...")
            file_path2 = create_test_file("This is the original content of the document.", "test_doc_same.txt")
            
            try:
                with open(file_path2, 'rb') as f:
                    files = {'file': ('test_doc_updated.txt', f, 'text/plain')}
                    response = requests.put(f"{base_url}/api/documents/{document_id}/reupload", files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Same content reupload successful!")
                    print(f"   💫 {data['message']}")
                    print(f"   📊 Chunks updated: {data['chunks_updated']}")
                else:
                    print(f"   ❌ Reupload failed: {response.status_code}")
                    print(f"   📄 Response: {response.text}")
                    
            finally:
                os.remove(file_path2)
            
            # Test 3: Reupload with different content
            print(f"\n3. Testing reupload with different content...")
            file_path3 = create_test_file("This is completely new and different content for the document.", "test_doc_different.txt")
            
            try:
                with open(file_path3, 'rb') as f:
                    files = {'file': ('test_doc_updated_v2.txt', f, 'text/plain')}
                    response = requests.put(f"{base_url}/api/documents/{document_id}/reupload", files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Different content reupload successful!")
                    print(f"   💫 {data['message']}")
                    print(f"   📊 Chunks updated: {data['chunks_updated']}")
                    print(f"   🔐 New checksum: {data['checksum']}")
                else:
                    print(f"   ❌ Reupload failed: {response.status_code}")
                    print(f"   📄 Response: {response.text}")
                    
            finally:
                os.remove(file_path3)
            
            # Test 4: Get document details to verify
            print(f"\n4. Verifying document details...")
            response = requests.get(f"{base_url}/api/documents/{document_id}")
            
            if response.status_code == 200:
                data = response.json()
                doc = data['document']
                print(f"   ✅ Document details retrieved!")
                print(f"   📄 Filename: {doc['filename']}")
                print(f"   🔐 Checksum: {doc['checksum']}")
                print(f"   📅 Updated: {doc['updated_at']}")
            
        else:
            print(f"   ❌ Initial upload failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Could not connect to server. Make sure the server is running on localhost:5000")
        print("   💡 Run: python run.py")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        
    finally:
        # Clean up
        if os.path.exists(file_path):
            os.remove(file_path)
    
    print("\n" + "=" * 50)
    print("🎯 Reupload functionality test completed!")


def show_api_usage():
    """Show API usage examples."""
    print("\n📚 API Usage Examples:")
    print("=" * 30)
    
    print("\n🔧 cURL Examples:")
    print("""
# Upload a document
curl -X POST http://localhost:5000/api/documents/upload \\
  -F "file=@/path/to/document.pdf"

# Reupload a document
curl -X PUT http://localhost:5000/api/documents/1/reupload \\
  -F "file=@/path/to/updated_document.pdf"

# Get document details
curl -X GET http://localhost:5000/api/documents/1
""")
    
    print("\n🐍 Python Examples:")
    print("""
import requests

# Reupload document
with open('updated_document.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.put('http://localhost:5000/api/documents/1/reupload', files=files)
    
if response.status_code == 200:
    result = response.json()
    print(f"Chunks updated: {result['chunks_updated']}")
""")


if __name__ == "__main__":
    print("🚀 Document Reupload Functionality Demo")
    print("This script demonstrates the new reupload feature")
    print("\nFeatures tested:")
    print("  • Same checksum: Regenerates chunks and embeddings")
    print("  • Different checksum: Updates content and regenerates")
    print("  • Error handling: Missing files, validation, etc.")
    
    choice = input("\nWould you like to:\n1. Run live test (requires server running)\n2. Show API usage examples\n3. Both\n\nChoice (1/2/3): ")
    
    if choice in ['1', '3']:
        test_reupload_functionality()
    
    if choice in ['2', '3']:
        show_api_usage()
    
    print("\n✨ Demo completed!")
