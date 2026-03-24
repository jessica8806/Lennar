from __future__ import annotations

import re
import uuid
from dataclasses import dataclass

from .connectors.models import AgendaItemRecord, MeetingRecord
from .signal_models import SummarySource, SignalCategory, SignalConfidence, SignalRecord, validate_signal


CATEGORY_KEYWORDS: dict[SignalCategory, list[str]] = {
    SignalCategory.HOUSING_DEVELOPMENT: ["housing", "development", "residential", "builder", "subdivision"],
    SignalCategory.ZONING_LAND_USE: ["zoning", "land use", "rezone", "variance", "specific plan"],
    SignalCategory.CAPITAL_PROJECTS: ["capital improvement", "cip", "facility expansion", "public works project"],
    SignalCategory.INFRASTRUCTURE_UTILITIES: ["utility", "water", "sewer", "storm drain", "infrastructure"],
    SignalCategory.PROCUREMENT_CONTRACTS: ["contract", "rfp", "procurement", "bid award", "vendor"],
    SignalCategory.FINANCE_BONDS: ["bond", "financing", "debt", "assessment district"],
    SignalCategory.FEES_TAXES: ["fee", "tax", "assessment", "rate adjustment"],
    SignalCategory.POLICY_ORDINANCES: ["ordinance", "policy", "resolution", "code amendment"],
    SignalCategory.PUBLIC_SAFETY: ["police", "fire", "emergency", "public safety"],
    SignalCategory.PARKS_RECREATION: ["park", "recreation", "trail", "community center"],
    SignalCategory.LEGAL_LITIGATION: ["litigation", "settlement", "claim", "legal"],
    SignalCategory.PERSONNEL_HR: ["personnel", "hr", "collective bargaining", "staffing"],
}


@dataclass(frozen=True)
class SignalGenerationInput:
    city: str
    meeting: MeetingRecord
    agenda_item: AgendaItemRecord
    supporting_documents: list[str]
    staff_report_text: str | None = None
    agenda_packet_text: str | None = None


def _normalize(value: str | None) -> str:
    return re.sub(r"\s+", " ", (value or "").strip().lower())


BOILERPLATE_PHRASES = {
    "public hearing",
    "consent calendar",
    "regular meeting",
    "agenda item",
    "discussion and action",
    "not available",
}


LOW_SIGNAL_TITLES = {
    "procedural waiver",
    "reading folder",
    "minutes",
    "call to order",
    "roll call",
}


def _has_meaningful_content(value: str | None) -> bool:
    normalized = _normalize(value)
    if not normalized:
        return False
    if len(normalized) < 40:
        return False
    if normalized in BOILERPLATE_PHRASES:
        return False
    tokens = [token for token in re.split(r"[^a-z0-9]+", normalized) if token]
    return len(tokens) >= 8


def _choose_summary(payload: SignalGenerationInput) -> tuple[str, SummarySource, bool, list[str]]:
    notes: list[str] = []

    if _has_meaningful_content(payload.staff_report_text):
        return payload.staff_report_text.strip(), SummarySource.STAFF_REPORT, True, notes

    if _has_meaningful_content(payload.agenda_packet_text):
        return payload.agenda_packet_text.strip(), SummarySource.AGENDA_PACKET, True, notes

    if _has_meaningful_content(payload.agenda_item.summary):
        return (payload.agenda_item.summary or "").strip(), SummarySource.ITEM_DESCRIPTION, True, notes

    notes.append("Summary unavailable from staff report, agenda packet, or item description; using title-only fallback")
    return f"Title-only: {payload.agenda_item.title}", SummarySource.TITLE_ONLY, False, notes


def _is_low_signal_title(title: str) -> bool:
    normalized = _normalize(title)
    return any(phrase in normalized for phrase in LOW_SIGNAL_TITLES)


def _score_categories(title: str, summary: str) -> dict[SignalCategory, tuple[int, list[str]]]:
    scored: dict[SignalCategory, tuple[int, list[str]]] = {}
    normalized_title = _normalize(title)
    normalized_summary = _normalize(summary)

    for category, keywords in CATEGORY_KEYWORDS.items():
        points = 0
        matched: list[str] = []

        for keyword in keywords:
            if keyword in normalized_title:
                points += 3
                matched.append(keyword)
            elif keyword in normalized_summary:
                points += 1
                matched.append(keyword)

        if points > 0:
            scored[category] = (points, matched)

    return scored


def _confidence_from_score(score: int) -> SignalConfidence:
    if score >= 5:
        return SignalConfidence.HIGH
    if score >= 3:
        return SignalConfidence.MEDIUM
    return SignalConfidence.LOW


def _build_signal_id(city: str, meeting_id: str, agenda_item_id: str, category: SignalCategory) -> str:
    seed = f"{city}|{meeting_id}|{agenda_item_id}|{category.value}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, seed))


def generate_signals_for_agenda_item(payload: SignalGenerationInput) -> list[SignalRecord]:
    summary, summary_source, content_available, extraction_notes = _choose_summary(payload)
    title = payload.agenda_item.title
    scored_hits = _score_categories(title=title, summary=summary)

    source_urls = [
        value
        for value in [payload.meeting.source_url, payload.meeting.agenda_url, payload.meeting.minutes_url, payload.meeting.video_url]
        if value
    ]

    if _is_low_signal_title(title):
        categories_with_scores: list[tuple[SignalCategory, int, list[str]]] = [
            (SignalCategory.POLICY_ORDINANCES, 1, ["general_update"])
        ]
    else:
        ranked = sorted(
            ((category, score, keywords) for category, (score, keywords) in scored_hits.items()),
            key=lambda item: item[1],
            reverse=True,
        )

        if not ranked:
            categories_with_scores = [(SignalCategory.POLICY_ORDINANCES, 1, ["general_update"])]
        else:
            top_score = ranked[0][1]
            threshold = max(3, top_score - 1)
            selected = [row for row in ranked if row[1] >= threshold][:2]
            if not selected:
                selected = [ranked[0]]
            categories_with_scores = selected

    signals: list[SignalRecord] = []
    for category, score, matched_keywords in categories_with_scores:
        confidence = _confidence_from_score(score)
        signal_type = (matched_keywords[0] if matched_keywords else "general_update").replace(" ", "_")

        if summary_source == SummarySource.TITLE_ONLY:
            confidence = SignalConfidence.LOW
            signal_type = "general_update"

        signal = SignalRecord(
            signal_id=_build_signal_id(
                city=payload.city,
                meeting_id=payload.meeting.external_meeting_id,
                agenda_item_id=payload.agenda_item.external_agenda_item_id,
                category=category,
            ),
            city=payload.city,
            meeting_body=payload.meeting.meeting_body,
            meeting_date=payload.meeting.meeting_date,
            agenda_item_number=payload.agenda_item.item_number,
            signal_category=category,
            signal_type=signal_type,
            title=payload.agenda_item.title,
            summary=summary,
            summary_source=summary_source,
            content_available=content_available,
            confidence=confidence,
            project_entity_id=None,
            supporting_documents=payload.supporting_documents,
            source_urls=source_urls,
            extraction_notes=extraction_notes,
        )
        validate_signal(signal)
        signals.append(signal)

    return signals
