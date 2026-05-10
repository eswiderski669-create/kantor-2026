"""Extract plain text from PDF, DOCX, and TXT uploads."""

from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader

ALLOWED_EXTENSIONS: frozenset[str] = frozenset({".pdf", ".docx", ".txt"})


class DocumentProcessingError(Exception):
    """Raised when a file cannot be parsed into text."""


class UnsupportedFormatError(DocumentProcessingError):
    """File extension is not allowed."""


def normalize_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def assert_allowed_extension(filename: str) -> str:
    ext = normalize_extension(filename)
    if ext not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        msg = f"Unsupported file type {ext!r}. Allowed: {allowed}."
        raise UnsupportedFormatError(msg)
    return ext


def extract_text(content: bytes, original_filename: str) -> str:
    ext = assert_allowed_extension(original_filename)
    try:
        if ext == ".txt":
            return _extract_txt(content)
        if ext == ".pdf":
            return _extract_pdf(content)
        if ext == ".docx":
            return _extract_docx(content)
    except UnsupportedFormatError:
        raise
    except Exception as exc:  # noqa: BLE001 — surface as a single processing error type
        msg = f"Failed to parse document: {exc}"
        raise DocumentProcessingError(msg) from exc
    raise DocumentProcessingError("Unknown document type")


def _extract_txt(content: bytes) -> str:
    text = content.decode("utf-8", errors="replace")
    return _normalize_whitespace(text)


def _extract_pdf(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    parts: list[str] = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception as exc:  # noqa: BLE001
            raise DocumentProcessingError(f"PDF page extract failed: {exc}") from exc
    return _normalize_whitespace("\n".join(parts))


def _extract_docx(content: bytes) -> str:
    doc = DocxDocument(BytesIO(content))
    parts = [p.text for p in doc.paragraphs if p.text]
    return _normalize_whitespace("\n".join(parts))


def _normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t\f\v]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
