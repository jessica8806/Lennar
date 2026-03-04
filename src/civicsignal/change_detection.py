from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

from .connectors.models import DocumentRecord, MeetingRecord


def _canonical_text(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.split()).strip().lower()


def _hash_payload(payload: dict[str, str]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def meeting_hash(meeting: MeetingRecord) -> str:
    payload = {
        "meeting_date": _canonical_text(meeting.meeting_date),
        "meeting_title": _canonical_text(meeting.meeting_title),
        "meeting_body": _canonical_text(meeting.meeting_body),
        "agenda_url": _canonical_text(meeting.agenda_url),
        "minutes_url": _canonical_text(meeting.minutes_url),
        "video_url": _canonical_text(meeting.video_url),
        "source_url": _canonical_text(meeting.source_url),
    }
    return _hash_payload(payload)


def document_hash(document: DocumentRecord) -> str:
    payload = {
        "document_type": document.document_type.value,
        "file_url": _canonical_text(document.file_url),
        "file_name": _canonical_text(document.file_name),
        "file_size_bytes": str(document.file_size_bytes),
        "linked_agenda_item_id": _canonical_text(document.linked_agenda_item_id),
    }
    return _hash_payload(payload)


@dataclass(frozen=True)
class ChangeEvent:
    entity_type: str
    entity_id: str
    event_type: str
    previous_hash: str | None
    current_hash: str


@dataclass(frozen=True)
class ChangeDetectionResult:
    events: list[ChangeEvent] = field(default_factory=list)
    new_count: int = 0
    changed_count: int = 0
    unchanged_count: int = 0


def detect_changes(
    previous: dict[str, str],
    current: dict[str, str],
    entity_type: str,
) -> ChangeDetectionResult:
    events: list[ChangeEvent] = []
    new_count = 0
    changed_count = 0
    unchanged_count = 0

    for entity_id, current_hash in current.items():
        previous_hash = previous.get(entity_id)
        if previous_hash is None:
            events.append(
                ChangeEvent(
                    entity_type=entity_type,
                    entity_id=entity_id,
                    event_type="new",
                    previous_hash=None,
                    current_hash=current_hash,
                )
            )
            new_count += 1
            continue

        if previous_hash != current_hash:
            events.append(
                ChangeEvent(
                    entity_type=entity_type,
                    entity_id=entity_id,
                    event_type="changed",
                    previous_hash=previous_hash,
                    current_hash=current_hash,
                )
            )
            changed_count += 1
            continue

        events.append(
            ChangeEvent(
                entity_type=entity_type,
                entity_id=entity_id,
                event_type="unchanged",
                previous_hash=previous_hash,
                current_hash=current_hash,
            )
        )
        unchanged_count += 1

    return ChangeDetectionResult(
        events=events,
        new_count=new_count,
        changed_count=changed_count,
        unchanged_count=unchanged_count,
    )
