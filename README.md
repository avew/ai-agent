# Chat Agent - RAG-based Document Q&A System

A sophisticated Retrieval-Augmented Generation (RAG) system that enables users to upload documents and ask questions about their content using AI-powered search and generation capabilities.

## ✨ Features

- **Document Upload & Processing**: Support for PDF, TXT, DOCX, and Excel files
- **Intelligent Text Chunking**: Automatic document segmentation with configurable chunk sizes
- **Vector Search**: Semantic search using OpenAI embeddings
- **RAG Pipeline**: Context-aware question answering with GPT models
- **Document Re-upload**: Smart handling of duplicate documents with chunk replacement
- **Advanced Logging**: Rolling file logs with daily rotation, size limits, and automatic compression
- **Database Integration**: PostgreSQL with automatic schema migrations
- **RESTful API**: Clean API endpoints for document management and chat

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL database
- OpenAI API key

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd chat-agent
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run the application**
```bash
python run.py
```

The application will be available at `http://localhost:5000`

## 📋 API Documentation

### Upload Document
```bash
POST /api/documents/upload
Content-Type: multipart/form-data

# Form data:
# file: [document file]
```

### Chat with Documents
```bash
POST /api/chat/
Content-Type: application/json

{
  "query": "Your question here",
  "top_k": 3  // Optional, default: 3
}
```

### List Documents
```bash
GET /api/documents/
```

### Delete Document
```bash
DELETE /api/documents/<document_id>
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

# Logging Configuration
LOG_LEVEL=INFO                 # DEBUG, INFO, WARNING, ERROR
ENABLE_FILE_LOGGING=true       # Enable/disable file logging
LOG_FILE=logs/app.log         # Log file path
LOG_BACKUP_COUNT=30           # Days of logs to keep
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Migration
AUTO_MIGRATE=true
```

## 📊 Advanced Logging

The application features sophisticated logging with:

### Rolling File Logs
- **Daily Rotation**: Automatically rotates at midnight
- **Size-based Rotation**: Rotates when file reaches 100MB
- **Compression**: Old logs are automatically compressed with gzip
- **Retention**: Configurable retention period (default: 30 days)
- **Cleanup**: Automatic removal of old log files

### Log Files Structure
```
logs/
├── app.log                    # Current active log
├── app.log.2025-06-11.gz     # Previous day (compressed)
├── app.log.2025-06-10.gz     # Older logs (compressed)
└── ...
```

### Monitoring Commands
```bash
# View current logs
tail -f logs/app.log

# View compressed logs
zcat logs/app.log.2025-06-11.gz | tail -100

# Search in compressed logs
zgrep "ERROR" logs/*.gz
```

## 🧩 Architecture

### Core Components

- **Document Service**: Handles file upload, processing, and storage
- **Embedding Service**: Generates vector embeddings using OpenAI
- **Search Service**: Performs semantic search with similarity scoring
- **Chat Service**: Implements RAG pipeline for question answering

### Database Schema

- **documents**: Document metadata and storage info
- **chunks**: Text chunks with embeddings for vector search

### Text Processing Pipeline

1. **Document Upload**: File validation and storage
2. **Text Extraction**: Content extraction from various file formats
3. **Chunking**: Intelligent text segmentation with overlap
4. **Embedding**: Vector generation using OpenAI embeddings
5. **Storage**: Chunks and embeddings stored in PostgreSQL

### RAG Pipeline

1. **Query Processing**: User question analysis
2. **Vector Search**: Semantic similarity search in document chunks
3. **Context Preparation**: Relevant chunks selection and formatting
4. **Generation**: AI-powered response using GPT with context
5. **Scoring**: Relevance scoring and quality metrics

## 🔍 Features Deep Dive

### Document Re-upload Handling
- Detects duplicate documents by filename
- Preserves document metadata
- Replaces old chunks with new ones
- Maintains referential integrity

### Intelligent Chunking
- Configurable chunk sizes and overlap
- Preserves document structure
- Optimized for embedding models
- Handles various document formats

### Search Quality Metrics
- Similarity scores for search results
- Relevance scoring for RAG responses
- Quality assessment (Excellent/Good/Fair/Poor)
- Comprehensive logging for monitoring

## 📈 Monitoring & Debugging

### Log Levels
- **DEBUG**: Detailed information including individual scores
- **INFO**: Standard operational information
- **WARNING**: Important notices and potential issues
- **ERROR**: Error conditions requiring attention

### Performance Metrics
- Search result similarity scores
- RAG pipeline relevance scores
- Query processing times
- Document processing statistics

### Health Checks
- Database connectivity
- OpenAI API availability
- File system permissions
- Log rotation status

## 🛠️ Development

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/test_comprehensive.py

# Test logging functionality
python test_rolling_logs.py
```

### Database Migrations
```bash
# Auto-migration (enabled by default)
AUTO_MIGRATE=true

# Manual migration
python migrate.py
```

### Development Environment
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run in debug mode
FLASK_DEBUG=true python run.py
```

## 🐳 Docker Support

```bash
# Build and run with Docker Compose
docker-compose up -d

# Build only
docker build -t chat-agent .

# Run container
docker run -p 5000:5000 --env-file .env chat-agent
```

## 📚 Documentation

- [Rolling Log Implementation](docs/ROLLING_LOG_IMPLEMENTATION.md)
- [Score Logging](docs/SCORE_LOGGING.md)
- [Chunking Implementation](docs/CHUNKING_IMPLEMENTATION.md)
- [Re-upload Functionality](docs/REUPLOAD_FUNCTIONALITY.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

**Copyright (c) 2025 Asep Rojali <aseprojali@gmail.com>**

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

See the [LICENSE](LICENSE) file for full details.

## 🙋‍♂️ Support

For questions, issues, or contributions, please:
- Check existing documentation
- Review log files for error details
- Open an issue with detailed information
- Include relevant log excerpts when reporting issues

---

**Note**: This application requires an OpenAI API key and PostgreSQL database. Ensure proper configuration before deployment.
