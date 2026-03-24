from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class SignalCategory(str, Enum):
    HOUSING_DEVELOPMENT = "Housing / Development"
    ZONING_LAND_USE = "Zoning / Land Use"
    CAPITAL_PROJECTS = "Capital Projects"
    INFRASTRUCTURE_UTILITIES = "Infrastructure / Utilities"
    PROCUREMENT_CONTRACTS = "Procurement / Contracts"
    FINANCE_BONDS = "Finance / Bonds"
    FEES_TAXES = "Fees / Taxes"
    POLICY_ORDINANCES = "Policy / Ordinances"
    PUBLIC_SAFETY = "Public Safety"
    PARKS_RECREATION = "Parks / Recreation"
    LEGAL_LITIGATION = "Legal / Litigation"
    PERSONNEL_HR = "Personnel / HR"


class SignalConfidence(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class SummarySource(str, Enum):
    STAFF_REPORT = "staff_report"
    AGENDA_PACKET = "agenda_packet"
    ITEM_DESCRIPTION = "item_description"
    TITLE_ONLY = "title_only"


@dataclass(frozen=True)
class SignalRecord:
    signal_id: str
    city: str
    meeting_body: str
    meeting_date: str
    agenda_item_number: str
    signal_category: SignalCategory
    signal_type: str
    title: str
    summary: str | None
    summary_source: SummarySource
    content_available: bool
    confidence: SignalConfidence
    project_entity_id: str | None
    supporting_documents: list[str] = field(default_factory=list)
    source_urls: list[str] = field(default_factory=list)
    extraction_notes: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    schema_version: str = "1.0.0"


def validate_signal(signal: SignalRecord) -> None:
    if not isinstance(signal.signal_category, SignalCategory):
        raise ValueError("signal_category must be a valid PRD category enum")
    if not isinstance(signal.confidence, SignalConfidence):
        raise ValueError("confidence must be High, Medium, or Low")
    if not signal.signal_id:
        raise ValueError("signal_id is required")
    if not signal.city:
        raise ValueError("city is required")
    if not signal.meeting_body:
        raise ValueError("meeting_body is required")
    if not signal.meeting_date:
        raise ValueError("meeting_date is required")
    if not signal.agenda_item_number:
        raise ValueError("agenda_item_number is required")
    if not signal.title:
        raise ValueError("title is required")
    if not isinstance(signal.summary_source, SummarySource):
        raise ValueError("summary_source must be a valid enum")
    if signal.summary_source == SummarySource.TITLE_ONLY and (not signal.summary or not signal.summary.startswith("Title-only:")):
        raise ValueError("title-only summaries must be explicitly labeled")
    if not signal.source_urls:
        raise ValueError("source_urls must include at least one source")
