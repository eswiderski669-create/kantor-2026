from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.documents.chunker import ChunkingConfigError
from app.core.documents.ingest import ingest_uploaded_bytes
from app.core.documents.processor import (
    DocumentProcessingError,
    UnsupportedFormatError,
)
from app.core.rag.chroma_index import ChromaIndexError
from app.core.rag.embedder import EmbeddingError
from app.db.session import get_db
from app.schemas.documents import DocumentUploadResponse

router = APIRouter(tags=["documents"])


def _preview_chunks(chunks: list[str]) -> list[str]:
    n = settings.document_preview_chunks
    cap = settings.document_preview_chunk_chars
    if n <= 0 or cap <= 0:
        return []
    out: list[str] = []
    for piece in chunks[:n]:
        piece = piece.strip()
        if len(piece) <= cap:
            out.append(piece)
        else:
            out.append(piece[:cap] + "...")
    return out


@router.post(
    "/documents/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    owner_id: uuid.UUID = Form(
        description="Owning user id (dev: use seeded dev user until JWT auth exists)"
    ),
    file: UploadFile = File(...),
    chunk_size: int | None = Query(
        None,
        ge=64,
        le=32000,
        description="Override default chunk size from settings",
    ),
    chunk_overlap: int | None = Query(
        None,
        ge=0,
        le=8000,
        description="Override default chunk overlap from settings",
    ),
    session: AsyncSession = Depends(get_db),
) -> DocumentUploadResponse:
    effective_chunk_size = chunk_size or settings.default_chunk_size
    effective_overlap = (
        chunk_overlap
        if chunk_overlap is not None
        else settings.default_chunk_overlap
    )

    content = await file.read()
    filename = file.filename or "unnamed"

    try:
        document, chunks, character_count = await ingest_uploaded_bytes(
            session,
            owner_id=owner_id,
            original_filename=filename,
            content=content,
            content_type=file.content_type,
            chunk_size=effective_chunk_size,
            chunk_overlap=effective_overlap,
        )
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except UnsupportedFormatError as exc:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=str(exc)) from exc
    except ChunkingConfigError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except DocumentProcessingError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except EmbeddingError as exc:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Embedding service unavailable: {exc}",
        ) from exc
    except ChromaIndexError as exc:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Vector store unavailable: {exc}",
        ) from exc

    return DocumentUploadResponse(
        document_id=document.id,
        original_filename=document.original_filename,
        status=document.status,
        byte_size=document.byte_size or 0,
        character_count=character_count,
        chunk_count=len(chunks),
        chroma_indexed_chunks=len(chunks),
        chroma_collection=settings.chroma_collection_name,
        chroma_document_id=document.chroma_document_id,
        chunk_size=effective_chunk_size,
        chunk_overlap=effective_overlap,
        storage_path=document.storage_path,
        preview_chunks=_preview_chunks(chunks),
    )
