"""Embedding generation via Ollama (e.g. nomic-embed-text)."""

from __future__ import annotations

import httpx

from app.config import settings


class EmbeddingError(RuntimeError):
    """Ollama embedding request failed or returned an unexpected payload."""


async def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    base = settings.ollama_base_url.rstrip("/")
    model = settings.ollama_embed_model
    timeout = httpx.Timeout(settings.ollama_embed_timeout_seconds)

    async with httpx.AsyncClient(timeout=timeout) as client:
        # Prefer /api/embed (batch). Older Ollama builds fall back to /api/embeddings per text.
        url_embed = f"{base}/api/embed"
        try:
            response = await client.post(
                url_embed,
                json={"model": model, "input": texts},
            )
        except httpx.RequestError as exc:
            msg = f"Ollama connection error: {exc}"
            raise EmbeddingError(msg) from exc

        if response.status_code == 200:
            return _parse_embed_response(response.json(), len(texts))

        if response.status_code != 404:
            msg = f"Ollama embed failed ({response.status_code}): {response.text[:500]}"
            raise EmbeddingError(msg)

        return await _embed_legacy_prompts(client, base, model, texts)


def _parse_embed_response(data: object, expected: int) -> list[list[float]]:
    if not isinstance(data, dict):
        msg = "Ollama embed response is not a JSON object"
        raise EmbeddingError(msg)

    raw: list[list[float]] | None = None
    if "embeddings" in data and isinstance(data["embeddings"], list):
        raw = data["embeddings"]
    elif "embedding" in data and isinstance(data["embedding"], list):
        raw = [data["embedding"]]

    if raw is None:
        msg = "Ollama embed response missing 'embeddings' or 'embedding'"
        raise EmbeddingError(msg)

    if len(raw) != expected:
        msg = f"Ollama returned {len(raw)} embeddings, expected {expected}"
        raise EmbeddingError(msg)

    out: list[list[float]] = []
    for i, vec in enumerate(raw):
        if not isinstance(vec, list):
            msg = f"Embedding at index {i} is not a list"
            raise EmbeddingError(msg)
        try:
            out.append([float(x) for x in vec])
        except (TypeError, ValueError) as exc:
            msg = f"Embedding at index {i} is not numeric"
            raise EmbeddingError(msg) from exc
    return out


async def _embed_legacy_prompts(
    client: httpx.AsyncClient,
    base: str,
    model: str,
    texts: list[str],
) -> list[list[float]]:
    url = f"{base}/api/embeddings"
    vectors: list[list[float]] = []
    for i, prompt in enumerate(texts):
        try:
            response = await client.post(
                url,
                json={"model": model, "prompt": prompt},
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            msg = f"Ollama embeddings failed for chunk {i}: {exc}"
            raise EmbeddingError(msg) from exc
        data = response.json()
        vec = data.get("embedding")
        if not isinstance(vec, list):
            msg = f"Ollama embeddings response missing 'embedding' for chunk {i}"
            raise EmbeddingError(msg)
        try:
            vectors.append([float(x) for x in vec])
        except (TypeError, ValueError) as exc:
            msg = f"Ollama embedding for chunk {i} is not numeric"
            raise EmbeddingError(msg) from exc
    return vectors
