# Tools Directory

Direktori ini berisi development tools, test scripts, dan demo scripts untuk aplikasi chat-agent.

## Files

### Test Scripts

#### `test_embedding_usage.py`
Comprehensive test untuk embedding usage logging system.

**Usage:**
```bash
python test_embedding_usage.py
```

**Features:**
- Test single text embedding
- Test batch chunks embedding  
- Test text chunking functionality
- Comprehensive logging demonstration

#### `test_manual_log.py`
Test untuk menambahkan manual log entry.

**Usage:**
```bash
python test_manual_log.py
```

#### `test_rolling_logs.py`
Test untuk rolling log functionality.

**Usage:**
```bash
python test_rolling_logs.py
```

#### `test_simple_log.py`
Simple test untuk log rotation functionality.

**Usage:**
```bash
python test_simple_log.py
```

#### `simple_test.py`
Basic test script untuk testing aplikasi.

### Demo Scripts

#### `demo_reupload.py`
Demo script untuk reupload functionality.

**Usage:**
```bash
python demo_reupload.py
```

**Features:**
- Demonstrasi upload dokumen
- Demonstrasi reupload dengan file yang sama
- Demonstrasi reupload dengan file yang berbeda
- API testing dengan requests

## Path Configuration

Scripts di direktori ini dikonfigurasi untuk:
- App imports: menggunakan `sys.path.insert(0, '..')`
- Environment files: `../.env`

Pastikan untuk menjalankan scripts dari direktori `tools/` atau adjust path sesuai kebutuhan.

## Dependencies

Scripts ini memerlukan:
- Flask app context (untuk test scripts)
- requests library (untuk demo scripts)
- dotenv untuk environment variables
