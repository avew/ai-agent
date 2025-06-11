-- Migration: 002_add_chunks_table.sql
-- Add document_chunks table for storing text chunks with embeddings
-- This allows for better retrieval with large documents

-- Create document_chunks table for storing individual chunks
CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL, -- Order of chunk within document
    content TEXT NOT NULL, -- Text content of the chunk
    embedding vector(1536), -- OpenAI text-embedding-3-small produces 1536-dimensional vectors
    token_count INTEGER NOT NULL, -- Number of tokens in this chunk
    start_char INTEGER NOT NULL, -- Starting character position in original document
    end_char INTEGER NOT NULL, -- Ending character position in original document
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_chunk_index ON document_chunks(document_id, chunk_index);
CREATE INDEX IF NOT EXISTS idx_document_chunks_token_count ON document_chunks(token_count);
CREATE INDEX IF NOT EXISTS idx_document_chunks_created_at ON document_chunks(created_at);

-- Create index for vector similarity search using cosine distance
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding_cosine ON document_chunks 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Create trigger to automatically update updated_at timestamp
CREATE TRIGGER update_document_chunks_updated_at 
    BEFORE UPDATE ON document_chunks 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Add unique constraint to prevent duplicate chunks
ALTER TABLE document_chunks 
ADD CONSTRAINT unique_document_chunk 
UNIQUE (document_id, chunk_index);

-- Insert comments about the schema
COMMENT ON TABLE document_chunks IS 'Stores text chunks of documents with their embeddings for fine-grained RAG search';
COMMENT ON COLUMN document_chunks.chunk_index IS 'Sequential index of chunk within the parent document';
COMMENT ON COLUMN document_chunks.token_count IS 'Number of tokens in this chunk for efficient retrieval';
COMMENT ON COLUMN document_chunks.start_char IS 'Starting character position in original document';
COMMENT ON COLUMN document_chunks.end_char IS 'Ending character position in original document';
