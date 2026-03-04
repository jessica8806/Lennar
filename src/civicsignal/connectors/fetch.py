from __future__ import annotations

import time
import urllib.error
import urllib.request
import ssl
from dataclasses import dataclass


DEFAULT_TIMEOUT_SECONDS = 20
DEFAULT_MAX_RETRIES = 2


@dataclass(frozen=True)
class FetchResult:
    html: str
    used_live_source: bool
    status_code: int | None = None
    fallback_reason: str | None = None


def fetch_html_with_fallback(
    url: str,
    fallback_html: str,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    max_retries: int = DEFAULT_MAX_RETRIES,
    verify_ssl: bool = True,
) -> FetchResult:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "CivicSignal/0.1 (+https://example.local)",
            "Accept": "text/html,application/xhtml+xml",
        },
    )

    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            ssl_context = None
            if not verify_ssl:
                ssl_context = ssl._create_unverified_context()

            with urllib.request.urlopen(request, timeout=timeout_seconds, context=ssl_context) as response:
                payload = response.read().decode("utf-8", errors="replace")
                status_code = getattr(response, "status", None)
                return FetchResult(html=payload, used_live_source=True, status_code=status_code)
        except (urllib.error.URLError, TimeoutError, ValueError) as error:
            last_error = error
            if attempt < max_retries:
                time.sleep(0.25 * (attempt + 1))

    reason = str(last_error) if last_error else "unknown_fetch_error"
    return FetchResult(html=fallback_html, used_live_source=False, status_code=None, fallback_reason=reason)
