-- Migration: 004_remove_documents_content.sql
-- Remove content column from documents table since content is now stored in document_chunks
-- This migration removes redundant data storage and reduces memory usage

-- Remove the content column from documents table
ALTER TABLE documents DROP COLUMN IF EXISTS content;

-- Update table comment to reflect the change
COMMENT ON TABLE documents IS 'Stores uploaded document metadata. Content is stored in document_chunks table for chunked retrieval';
