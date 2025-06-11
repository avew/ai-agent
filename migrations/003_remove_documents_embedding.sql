-- Migration: 003_remove_documents_embedding.sql
-- Remove embedding column from documents table since embeddings are now stored in document_chunks
-- This migration removes redundant data and simplifies the schema

-- Drop the vector similarity search index first
DROP INDEX IF EXISTS idx_documents_embedding_cosine;

-- Remove the embedding column from documents table
ALTER TABLE documents DROP COLUMN IF EXISTS embedding;

-- Update table comment to reflect the change
COMMENT ON TABLE documents IS 'Stores uploaded documents with their text content. Embeddings are stored in document_chunks table for chunked retrieval';
