# Embedding Cost Tracking System

## Overview

Sistem cost tracking untuk monitoring penggunaan embedding OpenAI telah diimplementasikan untuk membantu memantau biaya penggunaan API. Sistem ini mencatat setiap panggilan API embedding beserta detail penggunaannya.

## Features

### 1. Automatic Usage Logging
- 📊 **Token counting**: Menghitung jumlah token yang diproses
- 💰 **Cost calculation**: Kalkulasi biaya berdasarkan pricing model
- ⏱️ **Performance tracking**: Tracking waktu pemrosesan
- 🔢 **Request counting**: Menghitung jumlah API requests

### 2. Real-time Monitoring
- 🔍 **Live monitoring**: Monitor penggunaan secara real-time
- 📈 **Session tracking**: Tracking total penggunaan per session
- 🚨 **Instant notifications**: Notifikasi setiap operasi embedding

### 3. Historical Analysis
- 📅 **Daily analysis**: Analisis penggunaan per hari
- 🤖 **Model breakdown**: Breakdown penggunaan per model
- ⚙️ **Operation analysis**: Analisis per jenis operasi
- 📊 **Export capabilities**: Export data ke CSV

## Files Modified/Added

### Modified Files

#### `app/services/embedding_service.py`
- ➕ Added cost calculation methods
- ➕ Added usage logging functionality
- ➕ Enhanced error logging with cost information
- ➕ Added pricing configuration for different models

### New Files

#### `scripts/analyze_embedding_usage.py`
Script untuk menganalisis penggunaan embedding dari log files.

**Usage:**
```bash
# Analisis 30 hari terakhir (default)
cd scripts && python analyze_embedding_usage.py

# Analisis 7 hari terakhir
cd scripts && python analyze_embedding_usage.py --days 7

# Analisis dengan custom log file
cd scripts && python analyze_embedding_usage.py --log-file custom.log

# Export ke CSV
cd scripts && python analyze_embedding_usage.py --export-csv --output usage_report.csv
```

#### `scripts/monitor_embedding_usage.py`
Real-time monitor untuk penggunaan embedding.

**Usage:**
```bash
# Monitor dengan log file default
cd scripts && python monitor_embedding_usage.py

# Monitor dengan custom log file
cd scripts && python monitor_embedding_usage.py --log-file custom.log
```

#### `tools/test_embedding_usage.py`
Test script untuk demonstrasi embedding usage logging.

**Usage:**
```bash
cd tools && python test_embedding_usage.py
```

## Log Format

Sistem ini menambahkan log entries dengan format khusus:

```
EMBEDDING_USAGE | Operation: batch_chunks | Model: text-embedding-3-small | Tokens: 1,250 | Requests: 1 | Time: 0.850s | Cost: $0.000025 USD
```

### Log Components:
- **Operation**: Jenis operasi (`single_text`, `batch_chunks`)
- **Model**: Model embedding yang digunakan
- **Tokens**: Jumlah token yang diproses
- **Requests**: Jumlah API requests
- **Time**: Waktu pemrosesan dalam detik
- **Cost**: Estimasi biaya dalam USD

## Cost Calculation

### Pricing (per 1K tokens):
- `text-embedding-3-small`: $0.00002
- `text-embedding-3-large`: $0.00013
- `text-embedding-ada-002`: $0.0001

*Note: Harga dapat berubah, update nilai di `embedding_service.py` sesuai kebutuhan.*

### Formula:
```python
cost = (total_tokens / 1000.0) * price_per_1k_tokens
```

## Usage Examples

### 1. Run Test to Generate Sample Data
```bash
cd tools && python test_embedding_usage.py
```

### 2. Analyze Usage
```bash
# Quick analysis
cd scripts && python analyze_embedding_usage.py --days 1

# Detailed analysis with export
cd scripts && python analyze_embedding_usage.py --days 30 --export-csv
```

### 3. Real-time Monitoring
```bash
# Start monitoring (dalam terminal terpisah)
cd scripts && python monitor_embedding_usage.py

# Kemudian jalankan operasi embedding di terminal lain
cd tools && python test_embedding_usage.py
```

## Sample Output

### Analysis Report
```
📊 ANALISIS PENGGUNAAN EMBEDDING OPENAI
================================================================================

📈 RINGKASAN (30 hari terakhir)
   📅 Periode: 2025-06-12 sampai 2025-06-12
   💰 Total Cost: $0.000156 USD
   🎯 Total Tokens: 1,560
   📡 Total Requests: 3
   ⏱️  Total Time: 2.45 detik
   🔄 Total Operations: 3
   📊 Rata-rata Cost per 1K tokens: $0.000100
   📊 Rata-rata Tokens per Operation: 520.0
   📊 Rata-rata Time per Operation: 0.817s

🤖 PENGGUNAAN PER MODEL
   text-embedding-3-small:
      💰 Cost: $0.000156 (100.0%)
      🎯 Tokens: 1,560
      📡 Requests: 3
      🔄 Operations: 3
```

### Real-time Monitor
```
🔍 EMBEDDING USAGE MONITOR
========================================================================================================================
⏰ Time     | 🔄 Operation    | 🤖 Model               | 🎯   Tokens | 📡 Req | ⏱️   Time | 💰      Cost
------------------------------------------------------------------------------------------------------------------------
⏰ 14:30:15 | 🔄 single_text  | 🤖 text-embedding-3-small | 🎯      156 tokens | 📡   1 req | ⏱️  0.245s | 💰 $0.000003
⏰ 14:30:16 | 🔄 batch_chunks | 🤖 text-embedding-3-small | 🎯      890 tokens | 📡   1 req | ⏱️  0.634s | 💰 $0.000018
⏰ 14:30:17 | 🔄 batch_chunks | 🤖 text-embedding-3-small | 🎯      514 tokens | 📡   1 req | ⏱️  0.421s | 💰 $0.000010
```

## Integration with Existing Code

Sistem ini terintegrasi secara otomatis dengan kode yang sudah ada:

1. **Document Upload**: Saat upload dokumen, embedding akan di-log otomatis
2. **Chat Service**: Jika ada pencarian embedding, akan ter-log
3. **Batch Processing**: Operasi batch embedding akan ter-track

## Configuration

### Environment Variables
Tidak ada konfigurasi tambahan yang diperlukan. Sistem menggunakan konfigurasi logging yang sudah ada.

### Customization
- **Pricing**: Update nilai di `EmbeddingService.__init__()`
- **Log Format**: Modifikasi method `log_embedding_usage()`
- **Analysis Period**: Gunakan parameter `--days` di analyzer

## Best Practices

1. **Regular Monitoring**: Jalankan analysis secara berkala
2. **Cost Alerts**: Set up alerts jika cost melebihi threshold tertentu
3. **Model Optimization**: Gunakan model yang sesuai dengan kebutuhan
4. **Batch Processing**: Gunakan batch untuk efisiensi cost

## Troubleshooting

### Issue: Tidak ada data embedding usage
**Solution**: 
- Pastikan logging diaktifkan (`ENABLE_FILE_LOGGING=true`)
- Pastikan ada operasi embedding yang berjalan
- Check log file location (`LOG_FILE` in config)

### Issue: Cost calculation tidak akurat
**Solution**:
- Update pricing di `embedding_service.py`
- Pastikan token counting menggunakan model yang benar

### Issue: Real-time monitor tidak menampilkan data
**Solution**:
- Pastikan log file path benar
- Pastikan ada operasi embedding yang berjalan
- Check file permissions

## Future Enhancements

- 📊 Web dashboard untuk visualization
- 🚨 Email/Slack alerts untuk high usage
- 📈 Trend analysis dan forecasting
- 💾 Database storage untuk long-term tracking
- 🔄 Integration dengan billing systems
