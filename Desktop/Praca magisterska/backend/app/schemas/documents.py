from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    document_id: uuid.UUID
    original_filename: str
    status: str
    byte_size: int
    character_count: int
    chunk_count: int
    chroma_indexed_chunks: int = Field(
        description="Number of chunk vectors stored in ChromaDB (0 if document had no text chunks)"
    )
    chroma_collection: str = Field(description="Chroma collection name used for this project")
    chroma_document_id: str | None = Field(
        description="Logical document key stored with vectors (same as document_id when indexed)"
    )
    chunk_size: int = Field(description="Chunk size used for this ingest")
    chunk_overlap: int = Field(description="Chunk overlap used for this ingest")
    storage_path: str
    preview_chunks: list[str] = Field(
        description="Short previews of the first chunks (truncated for API payload size)"
    )
