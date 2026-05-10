"""Orchestrate save-on-disk + DB metadata + parse + chunk + Ollama embed + Chroma."""

from __future__ import annotations

import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.documents.chunker import ChunkingConfigError, chunk_text
from app.core.documents.processor import (
    DocumentProcessingError,
    assert_allowed_extension,
    extract_text,
)
from app.core.rag.chroma_index import ChromaIndexError, index_document_chunks
from app.core.rag.embedder import EmbeddingError, embed_texts
from app.models.document import Document
from app.models.user import User


async def ingest_uploaded_bytes(
    session: AsyncSession,
    *,
    owner_id: uuid.UUID,
    original_filename: str,
    content: bytes,
    content_type: str | None,
    chunk_size: int,
    chunk_overlap: int,
) -> tuple[Document, list[str], int]:
    if not await session.get(User, owner_id):
        msg = "Owner user does not exist"
        raise ValueError(msg)

    assert_allowed_extension(original_filename)
    if len(content) > settings.max_upload_bytes:
        msg = f"File exceeds max size of {settings.max_upload_bytes} bytes"
        raise ValueError(msg)

    ext = Path(original_filename).suffix.lower()[:16]
    doc_id = uuid.uuid4()
    stored_name = f"{doc_id}{ext}"
    relative_dir = str(doc_id)
    storage_relative = f"{relative_dir}/{stored_name}"

    base = settings.upload_dir.resolve()
    target_dir = base / relative_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / stored_name
    target_path.write_bytes(content)

    document = Document(
        id=doc_id,
        owner_id=owner_id,
        original_filename=Path(original_filename).name[:512],
        storage_path=storage_relative,
        content_type=content_type,
        byte_size=len(content),
        status="processing",
        chunk_count=None,
        last_error=None,
    )
    session.add(document)
    await session.flush()

    try:
        text = extract_text(content, original_filename)
        char_count = len(text)
        chunks = chunk_text(
            text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
    except (
        DocumentProcessingError,
        ChunkingConfigError,
    ) as exc:
        document.status = "failed"
        document.chunk_count = None
        document.last_error = str(exc)[:4000]
        await session.commit()
        raise
    except Exception as exc:  # noqa: BLE001
        document.status = "failed"
        document.last_error = str(exc)[:4000]
        await session.commit()
        raise

    document.chunk_count = len(chunks)

    if chunks:
        try:
            embeddings = await embed_texts(chunks)
            await index_document_chunks(
                document_id=doc_id,
                owner_id=owner_id,
                chunks=chunks,
                embeddings=embeddings,
            )
        except (EmbeddingError, ChromaIndexError, ValueError) as exc:
            document.status = "failed"
            document.last_error = str(exc)[:4000]
            document.chroma_document_id = None
            await session.commit()
            raise
        except Exception as exc:  # noqa: BLE001
            document.status = "failed"
            document.last_error = str(exc)[:4000]
            document.chroma_document_id = None
            await session.commit()
            raise

    document.status = "indexed"
    document.chroma_document_id = str(doc_id) if chunks else None
    document.last_error = None
    await session.commit()
    await session.refresh(document)
    return document, chunks, char_count
