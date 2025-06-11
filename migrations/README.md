# Database Migration untuk Chat Agent

Folder ini berisi migration file untuk setup database PostgreSQL dengan pgvector extension.

## Struktur File

- `001_initial_schema.sql` - SQL script untuk membuat tabel dan index
- `migrate.py` - Python script untuk menjalankan migration
- `README.md` - Dokumentasi migration

## Auto-Migration

Aplikasi Flask ini dilengkapi dengan **auto-migration** yang akan otomatis menjalankan migration saat aplikasi dimulai.

### Mengaktifkan Auto-Migration

Auto-migration diatur melalui environment variable `AUTO_MIGRATE` di file `.env`:

```env
AUTO_MIGRATE=true   # Aktifkan auto-migration (default)
AUTO_MIGRATE=false  # Nonaktifkan auto-migration
```

Ketika `AUTO_MIGRATE=true`, aplikasi akan:
1. Mengecek apakah tabel `documents` sudah ada
2. Jika belum ada, otomatis menjalankan migration `001_initial_schema.sql`
3. Memberikan log status migration

### Cara Kerja Auto-Migration

Saat menjalankan `python app.py`, aplikasi akan:

```bash
🔄 Running auto-migration check...
INFO:db_migrator:Checking database schema...
INFO:db_migrator:Documents table not found. Running initial migration...
INFO:db_migrator:Migration 001_initial_schema.sql executed successfully
INFO:db_migrator:✅ Initial migration completed successfully!
```

Atau jika database sudah siap:

```bash
🔄 Running auto-migration check...
INFO:db_migrator:Checking database schema...
INFO:db_migrator:✅ Database schema is up to date
```

## Prerequisites

1. PostgreSQL dengan pgvector extension
2. Python dependencies (sudah ada di requirements.txt)

### Install pgvector

**Option 1: Install dari source**
```bash
git clone --branch v0.7.4 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

**Option 2: Menggunakan Docker**
```bash
docker run -d \
  --name postgres-vector \
  -e POSTGRES_PASSWORD=yourpassword \
  -e POSTGRES_DB=chat \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

## Cara Menjalankan Migration

1. Pastikan file `.env` sudah dikonfigurasi dengan benar:
   ```
   DATABASE_URL=postgresql://user:password@host:port/dbname
   ```

2. Jalankan migration script:
   ```bash
   python migrate.py
   ```

## Schema Database

### Tabel `documents`

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PRIMARY KEY | Auto-increment ID |
| `filename` | VARCHAR(255) | Nama file yang diupload |
| `content` | TEXT | Konten teks dari file |
| `filepath` | VARCHAR(500) | Path file di storage |
| `checksum` | VARCHAR(64) | SHA-256 hash untuk deteksi duplikasi |
| `created_at` | TIMESTAMP | Waktu pembuatan record |
| `updated_at` | TIMESTAMP | Waktu update terakhir |

### Tabel `document_chunks`

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PRIMARY KEY | Auto-increment ID |
| `document_id` | INTEGER | Foreign key ke tabel documents |
| `chunk_index` | INTEGER | Urutan chunk dalam dokumen |
| `content` | TEXT | Konten teks chunk |
| `embedding` | vector(1536) | Vector embedding dari OpenAI |
| `token_count` | INTEGER | Jumlah token dalam chunk |
| `start_char` | INTEGER | Posisi karakter awal dalam dokumen |
| `end_char` | INTEGER | Posisi karakter akhir dalam dokumen |
| `created_at` | TIMESTAMP | Waktu pembuatan record |
| `updated_at` | TIMESTAMP | Waktu update terakhir |

### Indexes

- `idx_documents_filename` - Index pada kolom filename
- `idx_documents_checksum` - Index pada kolom checksum (unique)
- `idx_documents_created_at` - Index pada kolom created_at
- `idx_document_chunks_document_id` - Index pada kolom document_id
- `idx_document_chunks_chunk_index` - Index pada kombinasi document_id dan chunk_index
- `idx_document_chunks_embedding_cosine` - IVFFlat index untuk vector similarity search pada chunks

## Troubleshooting

### Error: pgvector extension not found

Install pgvector extension terlebih dahulu. Lihat prerequisites di atas.

### Error: Connection refused

Pastikan PostgreSQL sudah running dan konfigurasi DATABASE_URL sudah benar.

### Error: Permission denied

Pastikan user database memiliki permission untuk create extension dan create table.
