from __future__ import annotations

import io
import ssl
import time
import urllib.error
import urllib.request


def _load_pdf_reader():
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception:
        return None
    return PdfReader


def _download_document_bytes(
    url: str,
    timeout_seconds: int,
    max_retries: int,
    verify_ssl: bool,
) -> bytes | None:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "CivicSignal/0.1 (+https://example.local)",
            "Accept": "application/pdf,*/*",
        },
    )

    for attempt in range(max_retries + 1):
        try:
            ssl_context = None
            if not verify_ssl:
                ssl_context = ssl._create_unverified_context()

            with urllib.request.urlopen(request, timeout=timeout_seconds, context=ssl_context) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError, ValueError):
            if attempt < max_retries:
                time.sleep(0.25 * (attempt + 1))

    return None


def _extract_pdf_text(pdf_bytes: bytes, max_pages: int = 20, max_chars: int = 15000) -> str | None:
    if not pdf_bytes:
        return None

    pdf_reader_cls = _load_pdf_reader()
    if pdf_reader_cls is None:
        return None

    try:
        reader = pdf_reader_cls(io.BytesIO(pdf_bytes))
    except Exception:
        return None

    parts: list[str] = []
    for page in reader.pages[:max_pages]:
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        if text.strip():
            parts.append(text.strip())

    if not parts:
        return None

    combined = "\n".join(parts).strip()
    if not combined:
        return None
    if len(combined) > max_chars:
        return combined[:max_chars]
    return combined


def extract_agenda_packet_text(
    url: str,
    timeout_seconds: int,
    max_retries: int,
    verify_ssl: bool,
) -> str | None:
    payload = _download_document_bytes(
        url=url,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        verify_ssl=verify_ssl,
    )
    if payload is None:
        return None
    return _extract_pdf_text(payload)


def extract_item_context_from_packet(
    packet_text: str | None,
    item_title: str,
    max_chars: int = 2200,
) -> str | None:
    if not packet_text:
        return None

    normalized_packet = packet_text.lower()
    normalized_title = item_title.lower().strip()
    if not normalized_title:
        return packet_text[:max_chars]

    index = normalized_packet.find(normalized_title)
    if index < 0:
        return packet_text[:max_chars]

    start = max(0, index - 350)
    end = min(len(packet_text), index + len(item_title) + 1200)
    snippet = packet_text[start:end].strip()
    if not snippet:
        return packet_text[:max_chars]

    if len(snippet) > max_chars:
        return snippet[:max_chars]
    return snippet
