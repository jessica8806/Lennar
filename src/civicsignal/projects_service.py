from __future__ import annotations

import re
import uuid
from dataclasses import dataclass

from .signal_models import SignalRecord
from .signals_api import list_signals


@dataclass(frozen=True)
class ProjectTimelineEntry:
    signal_id: str
    meeting_date: str
    meeting_body: str
    signal_type: str
    signal_category: str
    confidence: str
    title: str


@dataclass(frozen=True)
class ProjectRecord:
    project_id: str
    project_name: str
    city: str
    first_detected: str
    latest_activity: str
    signals_count: int
    timeline: list[ProjectTimelineEntry]


@dataclass(frozen=True)
class ProjectsListResponse:
    items: list[ProjectRecord]
    total: int
    limit: int
    offset: int


_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "city",
    "council",
    "regular",
    "meeting",
    "agenda",
    "item",
    "approval",
    "adoption",
    "waive",
    "reading",
    "folder",
    "procedural",
}


def _clean_title(value: str) -> str:
    text = value.lower()
    text = re.sub(r"\d{2}-\d+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _project_key(signal: SignalRecord) -> str:
    tokens = [token for token in _clean_title(signal.title).split() if token not in _STOPWORDS]
    if len(tokens) >= 3:
        return " ".join(tokens[:5])
    if tokens:
        return " ".join(tokens)
    return f"{signal.signal_category.value.lower()} {signal.signal_type.lower()}"


def _project_name_from_key(key: str) -> str:
    return " ".join(word.capitalize() for word in key.split())


def _build_project_id(city: str, key: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"project|{city}|{key}"))


def _timeline_entry(signal: SignalRecord) -> ProjectTimelineEntry:
    return ProjectTimelineEntry(
        signal_id=signal.signal_id,
        meeting_date=signal.meeting_date,
        meeting_body=signal.meeting_body,
        signal_type=signal.signal_type,
        signal_category=signal.signal_category.value,
        confidence=signal.confidence.value,
        title=signal.title,
    )


def _build_projects(signals: list[SignalRecord]) -> list[ProjectRecord]:
    grouped: dict[tuple[str, str], list[SignalRecord]] = {}
    for signal in signals:
        key = _project_key(signal)
        grouped.setdefault((signal.city, key), []).append(signal)

    projects: list[ProjectRecord] = []
    for (city, key), records in grouped.items():
        timeline_signals = sorted(records, key=lambda row: row.meeting_date)
        timeline = [_timeline_entry(signal) for signal in timeline_signals]
        projects.append(
            ProjectRecord(
                project_id=_build_project_id(city=city, key=key),
                project_name=_project_name_from_key(key),
                city=city,
                first_detected=timeline_signals[0].meeting_date,
                latest_activity=timeline_signals[-1].meeting_date,
                signals_count=len(timeline_signals),
                timeline=timeline,
            )
        )

    projects.sort(key=lambda row: (row.latest_activity, row.signals_count), reverse=True)
    return projects


def list_projects(
    start_date: str,
    end_date: str,
    city: str | None = None,
    keyword: str | None = None,
    limit: int = 100,
    offset: int = 0,
    live_fetch: bool = False,
    timeout_seconds: int = 20,
    max_retries: int = 2,
    verify_ssl: bool = True,
) -> ProjectsListResponse:
    if limit < 1:
        raise ValueError("limit must be >= 1")
    if offset < 0:
        raise ValueError("offset must be >= 0")

    signals_response = list_signals(
        start_date=start_date,
        end_date=end_date,
        city=city,
        limit=10000,
        offset=0,
        live_fetch=live_fetch,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        verify_ssl=verify_ssl,
    )
    projects = _build_projects(signals_response.items)

    if keyword:
        lookup = keyword.lower()
        projects = [
            project
            for project in projects
            if lookup in project.project_name.lower()
            or any(lookup in entry.title.lower() for entry in project.timeline)
        ]

    total = len(projects)
    page = projects[offset : offset + limit]
    return ProjectsListResponse(items=page, total=total, limit=limit, offset=offset)


def get_project(
    project_id: str,
    start_date: str,
    end_date: str,
    city: str | None = None,
    live_fetch: bool = False,
    timeout_seconds: int = 20,
    max_retries: int = 2,
    verify_ssl: bool = True,
) -> ProjectRecord:
    response = list_projects(
        start_date=start_date,
        end_date=end_date,
        city=city,
        limit=10000,
        offset=0,
        live_fetch=live_fetch,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        verify_ssl=verify_ssl,
    )

    for project in response.items:
        if project.project_id == project_id:
            return project

    raise KeyError(f"Project not found: {project_id}")
