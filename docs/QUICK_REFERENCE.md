# Quick Reference - Chat Agent Project Structure

## 🚀 Quick Commands

### Embedding Cost Tracking
```bash
# Daily analysis
cd scripts && python analyze_embedding_usage.py --days 1

# Weekly analysis with CSV export
cd scripts && python analyze_embedding_usage.py --days 7 --export-csv

# Real-time monitoring
cd scripts && python monitor_embedding_usage.py
```

### Testing & Development
```bash
# Test embedding functionality
cd tools && python test_embedding_usage.py

# Test manual logging
cd tools && python test_manual_log.py

# Demo reupload feature
cd tools && python demo_reupload.py
```

### Run Application
```bash
# Development server
python run.py

# Or with Flask
python app.py
```

## 📁 Directory Structure

```
chat-agent/
├── 🏠 app/              # Core application code
├── 📚 docs/             # Documentation  
├── 📋 logs/             # Application logs
├── 🗃️ migrations/       # Database migrations
├── 📊 reports/          # Generated reports
├── ⚙️ scripts/          # Production utilities
├── 🧪 tests/            # Test suites
├── 🔧 tools/            # Development tools
├── 📎 uploads/          # User uploads
└── 🐍 venv/             # Virtual environment
```

## 🎯 Key Features

### ✅ Embedding Cost Tracking
- Automatic usage logging
- Real-time monitoring  
- Cost analysis & reporting
- CSV export for reporting

### ✅ Document Management
- Upload & processing
- Reupload functionality
- Chunking with overlap
- Vector storage

### ✅ Chat System
- RAG-based responses
- Relevance scoring
- Source attribution
- Query logging

### ✅ Configurable System Prompts
- System prompt environment configuration
- User prompt template customization
- Dynamic persona and format support
- Placeholder-based template system
- No code changes required

### ✅ Monitoring & Logging
- Rolling log files
- Request/response logging
- Performance metrics
- Error tracking

## 🛠️ Development Workflow

1. **Start Development**
   ```bash
   source venv/bin/activate
   python run.py
   ```

2. **Test New Features**
   ```bash
   cd tools && python test_*.py
   ```

3. **Monitor Usage**
   ```bash
   cd scripts && python monitor_embedding_usage.py
   ```

4. **Generate Reports**
   ```bash
   cd scripts && python analyze_embedding_usage.py --export-csv
   ```

## 📈 Cost Monitoring Commands

```bash
# Today's usage
cd scripts && python analyze_embedding_usage.py --days 1

# This week
cd scripts && python analyze_embedding_usage.py --days 7  

# This month
cd scripts && python analyze_embedding_usage.py --days 30

# Export for management
cd scripts && python analyze_embedding_usage.py --days 30 --export-csv --output ../reports/monthly_report.csv
```

## 🤖 System Prompt Configuration

```bash
# Set custom system prompt in .env
echo 'SYSTEM_PROMPT="Your custom AI assistant instructions here"' >> .env

# Examples:
# Business Assistant
SYSTEM_PROMPT="Anda adalah konsultan bisnis profesional. Berikan analisis strategis berdasarkan knowledge base."

# Technical Support  
SYSTEM_PROMPT="You are a technical support specialist. Provide clear solutions from technical documentation."

# Educational Tutor
SYSTEM_PROMPT="Kamu adalah tutor yang sabar. Jelaskan konsep dengan contoh praktis dari materi pembelajaran."
```

📖 **Full Documentation**: `docs/SYSTEM_PROMPT_CONFIGURATION.md`

---
📅 **Last Updated**: June 12, 2025  
🔗 **Full Documentation**: `docs/`
