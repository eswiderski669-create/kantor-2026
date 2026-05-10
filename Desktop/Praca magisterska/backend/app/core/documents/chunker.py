"""Fixed-size text chunking with overlap (RAG retrieval unit)."""

from __future__ import annotations


class ChunkingConfigError(ValueError):
    """Invalid chunk_size / chunk_overlap combination."""


def chunk_text(
    text: str,
    *,
    chunk_size: int,
    chunk_overlap: int,
) -> list[str]:
    if chunk_size < 1:
        msg = "chunk_size must be at least 1"
        raise ChunkingConfigError(msg)
    if chunk_overlap < 0:
        msg = "chunk_overlap must be non-negative"
        raise ChunkingConfigError(msg)
    if chunk_overlap >= chunk_size:
        msg = "chunk_overlap must be smaller than chunk_size"
        raise ChunkingConfigError(msg)

    cleaned = text.strip()
    if not cleaned:
        return []

    chunks: list[str] = []
    start = 0
    length = len(cleaned)
    step = chunk_size - chunk_overlap

    while start < length:
        end = min(start + chunk_size, length)
        piece = cleaned[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= length:
            break
        start += step

    return chunks
