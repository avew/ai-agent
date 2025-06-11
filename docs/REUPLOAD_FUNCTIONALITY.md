# Document Reupload Functionality

## Overview

The reupload functionality allows you to update an existing document by uploading a new version. The system intelligently handles the process based on the file's checksum:

- **Same checksum**: If the new file has the same checksum as the existing document, the system will delete all existing chunks and regenerate embeddings from the file content.
- **Different checksum**: If the new file has a different checksum, the system will update the document with the new content, delete old chunks, and generate new embeddings.

## API Endpoint

### PUT /api/documents/{document_id}/reupload

Reupload a document by its ID.

#### Parameters

- `document_id` (path parameter): The ID of the document to reupload
- `file` (form data): The new file to upload

#### Request Example

```bash
curl -X PUT \
  http://localhost:5000/api/documents/1/reupload \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@/path/to/your/updated_document.pdf'
```

#### Response Examples

**Success Response (200 OK):**
```json
{
  "message": "Document chunks and embeddings updated successfully",
  "document_id": 1,
  "filename": "updated_document.pdf",
  "checksum": "abc123def456",
  "chunks_updated": 15
}
```

**Error Responses:**

*Document not found (404):*
```json
{
  "error": "Document not found"
}
```

*No file uploaded (400):*
```json
{
  "error": "No file uploaded"
}
```

*Duplicate content (409):*
```json
{
  "error": "A document with this content already exists"
}
```

## Use Cases

### 1. Regenerating Embeddings
If you want to regenerate embeddings for an existing document (e.g., after improving your embedding model), simply reupload the same file. The system will:
- Detect the same checksum
- Delete existing chunks
- Regenerate chunks and embeddings
- Update the vector database

### 2. Updating Document Content
When you have a new version of a document with different content:
- Upload the new file
- System detects different checksum
- Replaces old content with new content
- Generates new chunks and embeddings
- Updates the vector database

## Technical Details

### Process Flow

1. **Validation**: Validates the uploaded file and checks if the document exists
2. **Checksum Calculation**: Calculates checksum of the new file
3. **Comparison**: Compares with existing document's checksum
4. **Processing**:
   - Same checksum: Regenerate chunks and embeddings
   - Different checksum: Update document with new content
5. **Database Update**: Updates document metadata and replaces chunks
6. **File Management**: Replaces old file with new file

### Error Handling

The system includes comprehensive error handling for:
- Missing files
- Invalid file formats
- Database errors
- File system errors
- Duplicate content detection

### Database Operations

The reupload process performs these database operations:
1. Delete existing document chunks
2. Update document metadata (filename, filepath, checksum, updated_at)
3. Insert new chunks with updated embeddings
4. Maintain referential integrity

## Integration Examples

### Python Example
```python
import requests

def reupload_document(document_id, file_path):
    url = f"http://localhost:5000/api/documents/{document_id}/reupload"
    
    with open(file_path, 'rb') as file:
        files = {'file': file}
        response = requests.put(url, files=files)
        
    if response.status_code == 200:
        result = response.json()
        print(f"Successfully reuploaded document {result['document_id']}")
        print(f"Updated {result['chunks_updated']} chunks")
        return result
    else:
        print(f"Error: {response.json()['error']}")
        return None

# Usage
result = reupload_document(1, '/path/to/updated_document.pdf')
```

### JavaScript Example
```javascript
async function reuploadDocument(documentId, file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`/api/documents/${documentId}/reupload`, {
            method: 'PUT',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            console.log(`Successfully reuploaded document ${result.document_id}`);
            console.log(`Updated ${result.chunks_updated} chunks`);
            return result;
        } else {
            console.error(`Error: ${result.error}`);
            return null;
        }
    } catch (error) {
        console.error('Network error:', error);
        return null;
    }
}

// Usage with file input
const fileInput = document.getElementById('file-input');
const documentId = 1;

fileInput.addEventListener('change', async (event) => {
    const file = event.target.files[0];
    if (file) {
        await reuploadDocument(documentId, file);
    }
});
```

## Benefits

1. **Efficient Vector Updates**: No need to delete and recreate documents
2. **Preserves Document ID**: Maintains references in other parts of your system
3. **Smart Processing**: Handles same vs. different content intelligently
4. **Atomic Operations**: Database transactions ensure data consistency
5. **Error Recovery**: Comprehensive error handling and cleanup
