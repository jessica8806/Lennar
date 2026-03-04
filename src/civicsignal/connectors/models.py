from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


MAX_DOCUMENT_SIZE_BYTES = 25 * 1024 * 1024


class PlatformType(str, Enum):
    GRANICUS = "granicus"
    LEGISTAR = "legistar"
    LASERFICHE = "laserfiche"
    NOVUSAGENDA = "novusagenda"
    ONBASE = "onbase"
    CIVICPLUS = "civicplus"


class DocumentType(str, Enum):
    AGENDA = "agenda"
    AGENDA_PACKET = "agenda_packet"
    STAFF_REPORT = "staff_report"
    ATTACHMENT = "attachment"


@dataclass(frozen=True)
class DateRange:
    start_date: str
    end_date: str


@dataclass(frozen=True)
class ConnectorRequest:
    city_id: str
    city_name: str
    platform_type: PlatformType
    discovery_url: str
    bodies: list[str]
    date_range: DateRange
    dry_run: bool = False
    live_fetch: bool = False
    timeout_seconds: int = 20
    max_retries: int = 2
    verify_ssl: bool = True
    debug_meetings: bool = False


@dataclass(frozen=True)
class MeetingRecord:
    external_meeting_id: str
    meeting_date: str
    meeting_title: str
    meeting_body: str
    agenda_url: Optional[str]
    minutes_url: Optional[str]
    video_url: Optional[str]
    source_url: str


@dataclass(frozen=True)
class AgendaItemRecord:
    external_agenda_item_id: str
    item_number: str
    title: str
    summary: Optional[str]
    action: Optional[str]
    vote_result: Optional[str]


@dataclass(frozen=True)
class DocumentRecord:
    external_document_id: str
    document_type: DocumentType
    file_url: str
    file_name: str
    file_size_bytes: int
    linked_agenda_item_id: Optional[str] = None


@dataclass(frozen=True)
class ConnectorError:
    error_code: str
    platform_type: PlatformType
    city_id: str
    body_name: str
    source_url: str
    message: str
    retryable: bool


@dataclass(frozen=True)
class DryRunMetrics:
    meetings_discovered: int = 0
    meetings_parsed: int = 0
    meeting_detail_200_count: int = 0
    agenda_items_parsed: int = 0
    documents_referenced: int = 0
    documents_downloaded: int = 0
    documents_text_extracted_ok: int = 0
    signals_generated: int = 0
    signals_title_only: int = 0
    signals_content_available: int = 0
    errors_count: int = 0
    runtime_ms: int = 0


@dataclass(frozen=True)
class DiscoverMeetingsResult:
    meetings: list[MeetingRecord] = field(default_factory=list)
    metrics: DryRunMetrics = field(default_factory=DryRunMetrics)


@dataclass(frozen=True)
class ParseAgendaResult:
    agenda_items: list[AgendaItemRecord] = field(default_factory=list)
    metrics: DryRunMetrics = field(default_factory=DryRunMetrics)


@dataclass(frozen=True)
class ExtractDocumentsResult:
    documents: list[DocumentRecord] = field(default_factory=list)
    metrics: DryRunMetrics = field(default_factory=DryRunMetrics)
