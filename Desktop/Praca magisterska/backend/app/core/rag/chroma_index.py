"""Write chunk embeddings and metadata to ChromaDB (HTTP server)."""

from __future__ import annotations

import asyncio
import uuid
from typing import Any

import chromadb

from app.config import settings


class ChromaIndexError(RuntimeError):
    """ChromaDB add/update failed."""


def _collection():
    client = chromadb.HttpClient(
        host=settings.chroma_host,
        port=settings.chroma_port,
    )
    return client.get_or_create_collection(
        name=settings.chroma_collection_name,
        metadata={"source": "corporate-rag-api"},
    )


def index_document_chunks_sync(
    *,
    document_id: uuid.UUID,
    owner_id: uuid.UUID,
    chunks: list[str],
    embeddings: list[list[float]],
) -> int:
    if len(chunks) != len(embeddings):
        msg = "chunks and embeddings length mismatch"
        raise ValueError(msg)
    if not chunks:
        return 0

    collection = _collection()
    doc_str = str(document_id)
    owner_str = str(owner_id)
    ids = [f"{doc_str}:{i}" for i in range(len(chunks))]
    metadatas: list[dict[str, Any]] = [
        {
            "document_id": doc_str,
            "chunk_index": i,
            "owner_id": owner_str,
        }
        for i in range(len(chunks))
    ]

    try:
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
        )
    except Exception as exc:  # noqa: BLE001
        msg = f"ChromaDB add failed: {exc}"
        raise ChromaIndexError(msg) from exc

    return len(chunks)


async def index_document_chunks(
    *,
    document_id: uuid.UUID,
    owner_id: uuid.UUID,
    chunks: list[str],
    embeddings: list[list[float]],
) -> int:
    return await asyncio.to_thread(
        index_document_chunks_sync,
        document_id=document_id,
        owner_id=owner_id,
        chunks=chunks,
        embeddings=embeddings,
    )


def delete_document_chunks_sync(document_id: uuid.UUID) -> None:
    """Remove all vectors for a document (id prefix document_id:)."""
    collection = _collection()
    doc_str = str(document_id)
    try:
        collection.delete(where={"document_id": doc_str})
    except Exception as exc:  # noqa: BLE001
        msg = f"ChromaDB delete failed: {exc}"
        raise ChromaIndexError(msg) from exc
