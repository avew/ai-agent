# Scripts Directory

Direktori ini berisi utility scripts untuk monitoring dan analisis aplikasi chat-agent.

## Files

### `analyze_embedding_usage.py`
Script untuk menganalisis penggunaan embedding OpenAI dari log files.

**Usage:**
```bash
# Analisis 30 hari terakhir (default)
python analyze_embedding_usage.py

# Analisis 7 hari terakhir  
python analyze_embedding_usage.py --days 7

# Analisis dengan custom log file
python analyze_embedding_usage.py --log-file custom.log

# Export ke CSV
python analyze_embedding_usage.py --export-csv --output usage_report.csv
```

**Features:**
- Analisis cost per hari/minggu/bulan
- Breakdown per model dan operation
- Export ke CSV untuk reporting
- Statistik detail penggunaan

### `monitor_embedding_usage.py`
Real-time monitor untuk penggunaan embedding OpenAI.

**Usage:**
```bash
# Monitor dengan log file default
python monitor_embedding_usage.py

# Monitor dengan custom log file
python monitor_embedding_usage.py --log-file custom.log
```

**Features:**
- Real-time monitoring penggunaan
- Live cost tracking
- Session statistics
- Graceful shutdown dengan Ctrl+C

## Path Configuration

Scripts di direktori ini dikonfigurasi untuk menggunakan path relatif:
- Log files: `../logs/app.log`
- Output reports: `../reports/`

Pastikan untuk menjalankan scripts dari direktori `scripts/` atau adjust path sesuai kebutuhan.
