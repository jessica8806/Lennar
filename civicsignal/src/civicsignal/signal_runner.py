from __future__ import annotations

from dataclasses import dataclass

from .city_registry import phase1_city_registry
from .connectors.models import ConnectorRequest, DateRange
from .connectors.registry import ConnectorRegistry
from .document_text import extract_agenda_packet_text, extract_item_context_from_packet
from .signal_engine import SignalGenerationInput, generate_signals_for_agenda_item
from .signal_models import SignalRecord


@dataclass(frozen=True)
class SignalRunSummary:
    city_id: str
    platform: str
    meetings_processed: int
    agenda_items_processed: int
    signals_generated: int


def run_signal_generation(
    start_date: str,
    end_date: str,
    city_id: str | None = None,
    live_fetch: bool = False,
    timeout_seconds: int = 20,
    max_retries: int = 2,
    verify_ssl: bool = True,
) -> tuple[list[SignalRunSummary], list[SignalRecord]]:
    registry = ConnectorRegistry.with_defaults()
    summaries: list[SignalRunSummary] = []
    all_signals: list[SignalRecord] = []

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

        agenda_items_processed = 0
        city_signals_generated = 0
        for meeting in discovered.meetings:
            agenda_result = connector.parse_agenda(request, meeting)
            document_result = connector.extract_documents(request, meeting)
            supporting_documents = [document.file_url for document in document_result.documents]
            agenda_packet_text: str | None = None

            if live_fetch:
                for document in document_result.documents:
                    if "View.ashx?M=A" not in document.file_url and "agenda" not in document.file_name.lower():
                        continue
                    agenda_packet_text = extract_agenda_packet_text(
                        url=document.file_url,
                        timeout_seconds=timeout_seconds,
                        max_retries=max_retries,
                        verify_ssl=verify_ssl,
                    )
                    if agenda_packet_text:
                        break

            for agenda_item in agenda_result.agenda_items:
                agenda_items_processed += 1
                item_context = extract_item_context_from_packet(
                    packet_text=agenda_packet_text,
                    item_title=agenda_item.title,
                )
                signals = generate_signals_for_agenda_item(
                    SignalGenerationInput(
                        city=city.city_id,
                        meeting=meeting,
                        agenda_item=agenda_item,
                        supporting_documents=supporting_documents,
                        agenda_packet_text=item_context,
                    )
                )
                city_signals_generated += len(signals)
                all_signals.extend(signals)

        summaries.append(
            SignalRunSummary(
                city_id=city.city_id,
                platform=city.platform_type.value,
                meetings_processed=len(discovered.meetings),
                agenda_items_processed=agenda_items_processed,
                signals_generated=city_signals_generated,
            )
        )

    return summaries, all_signals
