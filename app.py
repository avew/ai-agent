import os
import hashlib
import tempfile
import openai
import pandas as pd
from flask import Flask, abort, request, jsonify, send_file
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

from PyPDF2 import PdfReader
from docx import Document as DocxDocument
from db_migrator import DatabaseMigrator

# --- ENV SETUP ---
load_dotenv()  # Load environment variables from .env file
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")  # format: postgresql://user:pass@host/dbname
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
AUTO_MIGRATE = os.getenv("AUTO_MIGRATE", "true").lower() == "true"
# Ensure upload folder existsz
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

openai.api_key = OPENAI_API_KEY
engine = create_engine(DATABASE_URL, poolclass=NullPool)

app = Flask(__name__)

# --- Auto Migration on Startup ---
if AUTO_MIGRATE:
    try:
        print("🔄 Running auto-migration check...")
        migrator = DatabaseMigrator(DATABASE_URL)
        migrator.auto_migrate()
    except Exception as e:
        print(f"❌ Database migration check failed: {e}")
        print("⚠️  Application will continue, but database functionality may not work properly.")
        print("Please run migration manually: python migrate.py")
else:
    print("⏭️  Auto-migration disabled. Set AUTO_MIGRATE=true to enable.")

# --- Helper: Extract Text ---
def extract_text(file, filename):
    ext = filename.split('.')[-1].lower()
    if ext == 'pdf':
        reader = PdfReader(file)
        return '\n'.join(page.extract_text() for page in reader.pages if page.extract_text())
    elif ext == 'txt':
        return file.read().decode('utf-8')
    elif ext == 'docx':
        doc = DocxDocument(file)
        return '\n'.join([p.text for p in doc.paragraphs])
    elif ext in ('xls', 'xlsx'):
        df = pd.read_excel(file)
        return df.to_string(index=False)
    else:
        raise ValueError('Unsupported file type')

# --- Helper: Embedding ---
def get_embedding(text):
    resp = openai.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return resp.data[0].embedding

def get_checksum(file_path):
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

# --- Endpoint: Upload ---
@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    filename = file.filename

    # Simpan file ke folder uploads/
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)

    # Hitung checksum
    checksum = get_checksum(save_path)

    # Ekstrak isi file
    with open(save_path, "rb") as f:
        text_content = extract_text(f, filename)

    if not text_content.strip():
        os.remove(save_path)
        return jsonify({"error": "No content found in file"}), 400

    # Generate embedding
    embedding = get_embedding(text_content)
    embedding_pg = "[" + ",".join(str(x) for x in embedding) + "]"

    # Simpan ke DB
    with engine.begin() as conn:
        conn.execute(
            text("""INSERT INTO documents (filename, content, embedding, filepath, checksum) 
                    VALUES (:filename, :content, :embedding, :filepath, :checksum)"""),
            {"filename": filename, "content": text_content, "embedding": embedding_pg,
             "filepath": save_path, "checksum": checksum}
        )

    return jsonify({"status": "uploaded", "filename": filename, "path": save_path, "checksum": checksum})

@app.route("/files", methods=["GET"])
def list_files():
    with engine.connect() as conn:
        rows = conn.execute(text(
            "SELECT id, filename, filepath, checksum FROM documents ORDER BY id DESC"
        )).fetchall()
    result = []
    for r in rows:
        result.append({
            "id": r.id,
            "filename": r.filename,
            "filepath": r.filepath,
            "checksum": r.checksum,
            "download_url": f"/download/{r.id}"
        })
    return jsonify(result)

# --- Endpoint: Download ---
@app.route("/download/<int:file_id>", methods=["GET"])
def download_file(file_id):
    with engine.connect() as conn:
        doc = conn.execute(
            text("SELECT filename, filepath FROM documents WHERE id=:id"), {"id": file_id}
        ).fetchone()
    if not doc or not os.path.exists(doc.filepath):
        abort(404, description="File not found")
    return send_file(doc.filepath, as_attachment=True, download_name=doc.filename)

# --- Endpoint: Delete ---
@app.route("/delete/<int:file_id>", methods=["DELETE"])
def delete_file(file_id):
    with engine.begin() as conn:
        doc = conn.execute(
            text("SELECT filepath FROM documents WHERE id=:id"), {"id": file_id}
        ).fetchone()
        if not doc:
            return jsonify({"error": "File not found"}), 404
        # Hapus file dari storage
        try:
            if os.path.exists(doc.filepath):
                os.remove(doc.filepath)
        except Exception as e:
            return jsonify({"error": f"Failed to delete file: {str(e)}"}), 500
        # Hapus record dari db
        conn.execute(text("DELETE FROM documents WHERE id=:id"), {"id": file_id})
    return jsonify({"status": "deleted", "id": file_id})


# --- Helper: Search KB ---
def search_kb(query, top_k=3):
    q_embedding = get_embedding(query)
    embedding_pg = "[" + ",".join(str(x) for x in q_embedding) + "]"

    # v <=> q means cosine distance (pgvector syntax)
    sql = """
    SELECT id, filename, content, (embedding <=> :query_embedding) AS distance
    FROM documents
    ORDER BY distance ASC
    LIMIT :top_k
    """
    with engine.connect() as conn:
        rows = conn.execute(
            text(sql),
            {"query_embedding": embedding_pg, "top_k": top_k}
        ).fetchall()

    return [{"content": r.content, "filename": r.filename, "distance": r.distance} for r in rows]

# --- Endpoint: Chat (RAG) ---
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    query = data.get("query")
    if not query:
        return jsonify({"error": "query is required"}), 400

    # RAG: Retrieve relevant context
    contexts = search_kb(query)
    context_texts = "\n\n".join([c["content"][:1000] for c in contexts])  # truncate for safety

    # Generate answer using GPT-4o/mini
    prompt = f"""Konteks berikut diambil dari knowledge base:\n{context_texts}\n\nPertanyaan: {query}\nJawab dengan jelas dan akurat berdasarkan konteks di atas."""
    completion = openai.chat.completions.create(
        model="gpt-4o",  # gpt-4o adalah model "mini" paling optimal Juni 2025
        messages=[{"role": "system", "content": "Kamu adalah asisten AI yang membantu user menjawab berdasarkan knowledge base."},
                  {"role": "user", "content": prompt}],
        temperature=0.2
    )
    answer = completion.choices[0].message.content.strip()
    return jsonify({
        "query": query,
        "answer": answer,
        "sources": contexts
    })

# --- Main ---
if __name__ == "__main__":
    app.run(debug=True)
