from __future__ import annotations

from dataclasses import dataclass

from .signal_models import SignalConfidence, SignalRecord
from .signal_runner import run_signal_generation


@dataclass(frozen=True)
class SignalsListResponse:
    items: list[SignalRecord]
    total: int
    limit: int
    offset: int


def _parse_bool(value: bool | str | None) -> bool | None:
    if value is None or isinstance(value, bool):
        return value

    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "y"}:
        return True
    if normalized in {"false", "0", "no", "n"}:
        return False
    raise ValueError("content_available must be true or false")


def _confidence_rank(value: SignalConfidence) -> int:
    ranks = {
        SignalConfidence.HIGH: 3,
        SignalConfidence.MEDIUM: 2,
        SignalConfidence.LOW: 1,
    }
    return ranks[value]


def _matches_keyword(signal: SignalRecord, keyword: str | None) -> bool:
    if not keyword:
        return True

    haystack = " ".join(
        [
            signal.title,
            signal.signal_type,
            signal.city,
            signal.meeting_body,
            signal.summary or "",
        ]
    ).lower()
    return keyword.lower() in haystack


def list_signals(
    start_date: str,
    end_date: str,
    city: str | None = None,
    category: str | None = None,
    confidence: str | None = None,
    keyword: str | None = None,
    content_available: bool | str | None = None,
    sort_by: str = "date",
    sort_order: str = "desc",
    limit: int = 100,
    offset: int = 0,
    live_fetch: bool = False,
    timeout_seconds: int = 20,
    max_retries: int = 2,
    verify_ssl: bool = True,
) -> SignalsListResponse:
    if sort_by not in {"date", "confidence"}:
        raise ValueError("sort_by must be one of: date, confidence")
    if sort_order not in {"asc", "desc"}:
        raise ValueError("sort_order must be one of: asc, desc")
    if limit < 1:
        raise ValueError("limit must be >= 1")
    if offset < 0:
        raise ValueError("offset must be >= 0")

    _, all_signals = run_signal_generation(
        start_date=start_date,
        end_date=end_date,
        live_fetch=live_fetch,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        verify_ssl=verify_ssl,
    )

    category_filter = category.lower() if category else None
    confidence_filter = confidence.lower() if confidence else None
    content_filter = _parse_bool(content_available)

    filtered: list[SignalRecord] = []
    for signal in all_signals:
        if city and signal.city != city:
            continue
        if category_filter and signal.signal_category.value.lower() != category_filter:
            continue
        if confidence_filter and signal.confidence.value.lower() != confidence_filter:
            continue
        if content_filter is not None and signal.content_available != content_filter:
            continue
        if not _matches_keyword(signal, keyword):
            continue
        filtered.append(signal)

    reverse = sort_order == "desc"
    if sort_by == "date":
        filtered.sort(key=lambda signal: signal.meeting_date, reverse=reverse)
    else:
        filtered.sort(key=lambda signal: _confidence_rank(signal.confidence), reverse=reverse)

    total = len(filtered)
    end = offset + limit
    page = filtered[offset:end]

    return SignalsListResponse(items=page, total=total, limit=limit, offset=offset)


def get_signal(
    signal_id: str,
    start_date: str,
    end_date: str,
    live_fetch: bool = False,
    timeout_seconds: int = 20,
    max_retries: int = 2,
    verify_ssl: bool = True,
) -> SignalRecord:
    _, all_signals = run_signal_generation(
        start_date=start_date,
        end_date=end_date,
        live_fetch=live_fetch,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        verify_ssl=verify_ssl,
    )

    for signal in all_signals:
        if signal.signal_id == signal_id:
            return signal

    raise KeyError(f"Signal not found: {signal_id}")
