from __future__ import annotations

from dataclasses import dataclass

from .projects_service import list_projects
from .signal_models import SignalRecord
from .signals_api import list_signals


@dataclass(frozen=True)
class SearchSignalResult:
    signal_id: str
    title: str
    city: str
    meeting_date: str
    meeting_body: str
    category: str
    confidence: str


@dataclass(frozen=True)
class SearchProjectResult:
    project_id: str
    project_name: str
    city: str
    first_detected: str
    latest_activity: str
    signals_count: int


@dataclass(frozen=True)
class SearchMeetingResult:
    meeting_key: str
    city: str
    meeting_date: str
    meeting_body: str
    signals_count: int


@dataclass(frozen=True)
class SearchDocumentResult:
    document_url: str
    title: str
    city: str
    meeting_date: str
    meeting_body: str
    snippet: str


@dataclass(frozen=True)
class SearchResponse:
    query: str
    signals: list[SearchSignalResult]
    projects: list[SearchProjectResult]
    meetings: list[SearchMeetingResult]
    documents: list[SearchDocumentResult]


def _matches_query(value: str, query: str) -> bool:
    if not query:
        return True
    return query.lower() in value.lower()


def _signal_text(signal: SignalRecord) -> str:
    return " ".join(
        [
            signal.title,
            signal.summary or "",
            signal.meeting_body,
            signal.signal_type,
            signal.signal_category.value,
        ]
    )


def _snippet(signal: SignalRecord, query: str, max_chars: int = 180) -> str:
    text = (signal.summary or signal.title or "").strip()
    if not text:
        return ""
    if not query:
        return text[:max_chars]

    normalized_text = text.lower()
    normalized_query = query.lower()
    index = normalized_text.find(normalized_query)
    if index < 0:
        return text[:max_chars]

    start = max(0, index - 60)
    end = min(len(text), index + len(query) + 100)
    return text[start:end]


def search_index(
    start_date: str,
    end_date: str,
    query: str,
    city: str | None = None,
    meeting_body: str | None = None,
    category: str | None = None,
    confidence: str | None = None,
    live_fetch: bool = False,
    timeout_seconds: int = 20,
    max_retries: int = 2,
    verify_ssl: bool = True,
) -> SearchResponse:
    signals_response = list_signals(
        start_date=start_date,
        end_date=end_date,
        city=city,
        category=category,
        confidence=confidence,
        live_fetch=live_fetch,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        verify_ssl=verify_ssl,
        limit=10000,
        offset=0,
    )

    filtered_signals: list[SignalRecord] = []
    for signal in signals_response.items:
        if meeting_body and meeting_body.lower() not in signal.meeting_body.lower():
            continue
        if not _matches_query(_signal_text(signal), query):
            continue
        filtered_signals.append(signal)

    signal_results = [
        SearchSignalResult(
            signal_id=signal.signal_id,
            title=signal.title,
            city=signal.city,
            meeting_date=signal.meeting_date,
            meeting_body=signal.meeting_body,
            category=signal.signal_category.value,
            confidence=signal.confidence.value,
        )
        for signal in filtered_signals
    ]

    project_list = list_projects(
        start_date=start_date,
        end_date=end_date,
        city=city,
        keyword=query or None,
        live_fetch=live_fetch,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        verify_ssl=verify_ssl,
        limit=1000,
        offset=0,
    )
    project_results = [
        SearchProjectResult(
            project_id=project.project_id,
            project_name=project.project_name,
            city=project.city,
            first_detected=project.first_detected,
            latest_activity=project.latest_activity,
            signals_count=project.signals_count,
        )
        for project in project_list.items
    ]

    meetings_map: dict[tuple[str, str, str], int] = {}
    for signal in filtered_signals:
        key = (signal.city, signal.meeting_date, signal.meeting_body)
        meetings_map[key] = meetings_map.get(key, 0) + 1
    meeting_results = [
        SearchMeetingResult(
            meeting_key=f"{city_name}|{meeting_date}|{body}",
            city=city_name,
            meeting_date=meeting_date,
            meeting_body=body,
            signals_count=count,
        )
        for (city_name, meeting_date, body), count in sorted(meetings_map.items(), key=lambda row: row[0][1], reverse=True)
    ]

    documents_seen: set[str] = set()
    document_results: list[SearchDocumentResult] = []
    for signal in filtered_signals:
        for url in signal.supporting_documents:
            if url in documents_seen:
                continue
            documents_seen.add(url)
            document_results.append(
                SearchDocumentResult(
                    document_url=url,
                    title=signal.title,
                    city=signal.city,
                    meeting_date=signal.meeting_date,
                    meeting_body=signal.meeting_body,
                    snippet=_snippet(signal, query),
                )
            )

    return SearchResponse(
        query=query,
        signals=signal_results,
        projects=project_results,
        meetings=meeting_results,
        documents=document_results,
    )
