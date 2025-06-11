# Chat Agent - RAG-based Document Q&A System

A modern Flask application for document-based question answering using Retrieval Augmented Generation (RAG) with OpenAI's GPT models and PostgreSQL with pgvector.

## 🚀 Features

- **Document Upload & Processing**: Support for PDF, DOCX, TXT, XLS/XLSX files
- **Intelligent Text Chunking**: Automatic text splitting with token-based chunking for optimal embedding performance
- **Vector Search**: Semantic search using OpenAI embeddings and pgvector
- **RAG Chat**: Intelligent Q&A based on uploaded documents with chunk-level retrieval
- **RESTful API**: Clean, documented API endpoints
- **Auto Migration**: Automatic database schema setup
- **Modular Architecture**: Well-structured Flask application following best practices

## 🏗️ Architecture

```
chat-agent/
├── app/
│   ├── __init__.py          # Application factory
│   ├── config.py            # Configuration management
│   ├── models/              # Data models
│   ├── services/            # Business logic layer
│   │   ├── document_service.py    # Document operations with chunking
│   │   ├── embedding_service.py   # OpenAI embeddings with token-based chunking
│   │   └── search_service.py      # RAG functionality with chunk-level search
│   ├── routes/              # API endpoints
│   │   ├── documents.py     # Document CRUD operations
│   │   └── chat.py          # Chat/search endpoints
│   ├── utils/               # Utility functions
│   └── database/            # Database migrations
├── migrations/              # SQL migration files
├── tests/                   # Unit tests
├── uploads/                 # File storage
└── run.py                   # Application entry point
```

## 🛠️ Setup

### Prerequisites

1. **PostgreSQL with pgvector extension**
2. **Python 3.8+**
3. **OpenAI API Key**

### Installation

1. **Clone and setup environment:**
```bash
git clone <repository-url>
cd chat-agent
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Setup PostgreSQL with pgvector:**

**Option A: Using Docker**
```bash
docker run -d \
  --name postgres-vector \
  -e POSTGRES_PASSWORD=yourpassword \
  -e POSTGRES_DB=chat \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

**Option B: Install from source**
```bash
git clone --branch v0.7.4 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your settings:
# - OPENAI_API_KEY
# - DATABASE_URL
```

4. **Run the application:**
```bash
python run.py
```

The application will automatically run database migrations on startup if `AUTO_MIGRATE=true`.

## 📡 API Endpoints

### Health Check
```
GET /health                 # Application health
GET /api/chat/health       # Chat service health
GET /api                   # API information
```

### Documents
```
POST /api/documents/upload          # Upload document (with automatic chunking)
GET  /api/documents/               # List documents (paginated)
GET  /api/documents/{id}           # Get document details
GET  /api/documents/{id}/chunks    # Get document chunks information
GET  /api/documents/{id}/download  # Download document
DELETE /api/documents/{id}         # Delete document (and its chunks)
GET  /api/documents/stats          # Document and chunk statistics
```

### Chat & Search
```
POST /api/chat/            # RAG-based Q&A using chunk-level retrieval
POST /api/chat/search      # Document chunk search only
```

## 🔧 Configuration

Key configuration options in `.env`:

```env
# OpenAI
OPENAI_API_KEY=sk-...

# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Application
FLASK_ENV=development
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=true

# File Upload
UPLOAD_FOLDER=./uploads

# Text Chunking Configuration
MAX_TOKENS_PER_CHUNK=8000      # Maximum tokens per chunk
CHUNK_OVERLAP_TOKENS=200       # Overlap tokens between chunks

# Migration
AUTO_MIGRATE=true
```

## 🔧 Text Chunking System

The application features an intelligent text chunking system that automatically splits large documents into smaller, manageable pieces for optimal embedding and retrieval performance.

### How It Works

1. **Token-Based Splitting**: Documents are split based on token counts (default: 8,000 tokens per chunk)
2. **Sentence Boundaries**: Chunks respect sentence boundaries to maintain context
3. **Smart Overlap**: Configurable overlap between chunks (default: 200 tokens) ensures continuity
4. **Batch Embedding**: Multiple chunks are processed efficiently using OpenAI's batch API
5. **Chunk-Level Search**: Search operates at the chunk level for precise retrieval

### Configuration

```env
MAX_TOKENS_PER_CHUNK=8000      # Adjust based on your model's context window
CHUNK_OVERLAP_TOKENS=200       # Overlap for maintaining context between chunks
```

### Benefits

- **Better Retrieval**: Smaller chunks provide more precise search results
- **Token Efficiency**: Avoids hitting embedding model token limits
- **Context Preservation**: Overlapping ensures important information isn't lost at boundaries
- **Scalability**: Handles documents of any size efficiently

> 📋 **For detailed implementation details**, see [CHUNKING_IMPLEMENTATION.md](./docs/CHUNKING_IMPLEMENTATION.md)

## 📝 Usage Examples

### Upload Document
```bash
curl -X POST \
  -F "file=@document.pdf" \
  http://localhost:5000/api/documents/upload
```

### Ask Questions
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?"}' \
  http://localhost:5000/api/chat/
```

### Get Document Chunks
```bash
curl http://localhost:5000/api/documents/1/chunks
```

Response:
```json
{
  "document_id": 1,
  "chunks": [
    {
      "id": 1,
      "chunk_index": 0,
      "content": "Introduction to AI...",
      "token_count": 245,
      "start_char": 0,
      "end_char": 1200
    },
    {
      "id": 2,
      "chunk_index": 1,
      "content": "Machine Learning is...",
      "token_count": 312,
      "start_char": 1000,
      "end_char": 2500
    }
  ],
  "total_chunks": 2
}
```

### Get Statistics
```bash
curl http://localhost:5000/api/documents/stats
```

Response:
```json
{
  "total_documents": 5,
  "total_chunks": 23,
  "avg_tokens_per_chunk": 456.7,
  "total_tokens": 10504
}
```

### Search Document Chunks
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"query": "AI concepts", "top_k": 5}' \
  http://localhost:5000/api/chat/search
```

## 🧪 Testing

Run tests:
```bash
python -m pytest tests/ -v
```

Run specific test:
```bash
python -m pytest tests/test_app.py::HealthCheckTests -v
```

## 🔒 Security Considerations

- File upload validation and sanitization
- SQL injection prevention using parameterized queries
- Environment variable management for sensitive data
- File size limits and allowed extensions

## 📊 Performance

- Vector similarity search using pgvector IVFFlat index
- Connection pooling with SQLAlchemy
- Efficient text processing and chunking
- Configurable embedding batch processing

## 🚀 Deployment

### Using Docker (Recommended)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "run.py"]
```

### Using Gunicorn (Production)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

## 🤝 Contributing

1. Follow PEP 8 style guidelines
2. Add tests for new features
3. Update documentation
4. Use meaningful commit messages

## 📄 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Common Issues

1. **pgvector extension not found**
   - Install pgvector extension in PostgreSQL
   - Ensure proper permissions for creating extensions

2. **OpenAI API errors**
   - Verify API key is valid and has credits
   - Check rate limits and quotas

3. **File upload failures**
   - Check file size limits
   - Verify supported file formats
   - Ensure upload directory permissions

4. **Database connection issues**
   - Verify DATABASE_URL format
   - Check PostgreSQL service status
   - Ensure database exists and user has permissions

### Logs

Application logs provide detailed error information:
```bash
python run.py 2>&1 | tee app.log
```

### Manual Migration

If auto-migration fails:
```bash
python -m app.database.migrator
```
