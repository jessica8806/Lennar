from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .change_detection import detect_changes, document_hash, meeting_hash
from .change_store import ChangeSnapshotStore
from .city_registry import phase1_city_registry
from .connectors.models import ConnectorRequest, DateRange
from .connectors.registry import ConnectorRegistry


@dataclass(frozen=True)
class ChangeRunSummary:
    city_id: str
    platform: str
    meetings_new: int
    meetings_changed: int
    meetings_unchanged: int
    documents_new: int
    documents_changed: int
    documents_unchanged: int


def run_change_detection(
    start_date: str,
    end_date: str,
    city_id: str | None = None,
    live_fetch: bool = False,
    timeout_seconds: int = 20,
    max_retries: int = 2,
    verify_ssl: bool = True,
    state_path: str = ".civicsignal/change-state.json",
    persist: bool = True,
) -> list[ChangeRunSummary]:
    registry = ConnectorRegistry.with_defaults()
    store = ChangeSnapshotStore(Path(state_path))
    previous = store.load()
    previous_meeting_hashes = previous["meetings"]
    previous_document_hashes = previous["documents"]

    current_meeting_hashes = dict(previous_meeting_hashes)
    current_document_hashes = dict(previous_document_hashes)

    summaries: list[ChangeRunSummary] = []

    for city in phase1_city_registry():
        if city_id and city.city_id != city_id:
            continue

        request = ConnectorRequest(
            city_id=city.city_id,
            city_name=city.city_name,
            platform_type=city.platform_type,
            discovery_url=city.discovery_url,
            bodies=city.bodies,
            date_range=DateRange(start_date=start_date, end_date=end_date),
            dry_run=True,
            live_fetch=live_fetch,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            verify_ssl=verify_ssl,
        )

        connector = registry.resolve(city.platform_type)
        discovered = connector.discover_meetings(request)

        city_meeting_previous = {
            key: value for key, value in previous_meeting_hashes.items() if key.startswith(f"{city.city_id}:")
        }
        city_meeting_current: dict[str, str] = {}

        city_document_previous = {
            key: value for key, value in previous_document_hashes.items() if key.startswith(f"{city.city_id}:")
        }
        city_document_current: dict[str, str] = {}

        for meeting in discovered.meetings:
            meeting_key = f"{city.city_id}:{meeting.external_meeting_id}"
            city_meeting_current[meeting_key] = meeting_hash(meeting)

            documents = connector.extract_documents(request, meeting).documents
            for document in documents:
                document_key = f"{city.city_id}:{meeting.external_meeting_id}:{document.external_document_id}"
                city_document_current[document_key] = document_hash(document)

        meeting_delta = detect_changes(city_meeting_previous, city_meeting_current, entity_type="meeting")
        document_delta = detect_changes(city_document_previous, city_document_current, entity_type="document")

        current_meeting_hashes.update(city_meeting_current)
        current_document_hashes.update(city_document_current)

        summaries.append(
            ChangeRunSummary(
                city_id=city.city_id,
                platform=city.platform_type.value,
                meetings_new=meeting_delta.new_count,
                meetings_changed=meeting_delta.changed_count,
                meetings_unchanged=meeting_delta.unchanged_count,
                documents_new=document_delta.new_count,
                documents_changed=document_delta.changed_count,
                documents_unchanged=document_delta.unchanged_count,
            )
        )

    if persist:
        store.save(meetings=current_meeting_hashes, documents=current_document_hashes)

    return summaries
