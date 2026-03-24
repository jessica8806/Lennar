from __future__ import annotations

from dataclasses import dataclass, field

from .city_registry import phase1_city_registry
from .connectors.models import ConnectorRequest, DateRange, MAX_DOCUMENT_SIZE_BYTES
from .connectors.registry import ConnectorRegistry
from .document_text import extract_agenda_packet_text, extract_item_context_from_packet
from .signal_engine import SignalGenerationInput, generate_signals_for_agenda_item
from .signal_models import SummarySource


def _safe_rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


@dataclass(frozen=True)
class CityRunHealth:
    city_id: str
    platform: str
    meetings_discovered: int
    meetings_processed: int
    agenda_items_processed: int
    documents_discovered: int
    documents_downloaded: int
    documents_failed: int
    documents_skipped_size: int
    documents_parsed_text_ok: int
    documents_parsed_text_empty: int
    signals_generated: int
    signals_content_available_count: int
    signals_title_only_count: int
    content_availability_rate: float
    doc_parse_success_rate: float
    title_only_rate: float
    status: str
    admin_actions: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RunHealthSummary:
    cities: list[CityRunHealth]
    totals: CityRunHealth


def _evaluate_status(
    content_availability_rate: float,
    doc_parse_success_rate: float,
    connector_failure_count: int,
) -> str:
    if content_availability_rate < 0.10 or connector_failure_count > 0:
        return "failed"
    if content_availability_rate >= 0.50 or doc_parse_success_rate >= 0.80:
        return "healthy"
    return "warning"


def _build_admin_actions(signals_title_only_count: int, signals_generated: int) -> list[str]:
    actions: list[str] = []
    if signals_generated > 0:
        title_only_rate = _safe_rate(signals_title_only_count, signals_generated)
        if title_only_rate > 0.0:
            percentage = round(title_only_rate * 100, 1)
            actions.append(
                f"{percentage}% of signals are title-only — enable PDF extraction for agenda packets."
            )
    return actions


def _empty_city_record(city_id: str, platform: str) -> CityRunHealth:
    return CityRunHealth(
        city_id=city_id,
        platform=platform,
        meetings_discovered=0,
        meetings_processed=0,
        agenda_items_processed=0,
        documents_discovered=0,
        documents_downloaded=0,
        documents_failed=0,
        documents_skipped_size=0,
        documents_parsed_text_ok=0,
        documents_parsed_text_empty=0,
        signals_generated=0,
        signals_content_available_count=0,
        signals_title_only_count=0,
        content_availability_rate=0.0,
        doc_parse_success_rate=0.0,
        title_only_rate=0.0,
        status="failed",
        admin_actions=[],
    )


def run_system_health(
    start_date: str,
    end_date: str,
    city_id: str | None = None,
    live_fetch: bool = False,
    timeout_seconds: int = 20,
    max_retries: int = 2,
    verify_ssl: bool = True,
) -> RunHealthSummary:
    registry = ConnectorRegistry.with_defaults()
    city_summaries: list[CityRunHealth] = []

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

        meetings_discovered = len(discovered.meetings)
        meetings_processed = 0
        agenda_items_processed = 0
        documents_discovered = 0
        documents_downloaded = 0
        documents_failed = 0
        documents_skipped_size = 0
        documents_parsed_text_ok = 0
        documents_parsed_text_empty = 0
        signals_generated = 0
        signals_content_available_count = 0
        signals_title_only_count = 0

        for meeting in discovered.meetings:
            meetings_processed += 1
            agenda_result = connector.parse_agenda(request, meeting)
            agenda_items_processed += len(agenda_result.agenda_items)

            document_result = connector.extract_documents(request, meeting)
            documents_discovered += len(document_result.documents)

            supporting_documents: list[str] = []
            agenda_packet_text: str | None = None
            for document in document_result.documents:
                if document.file_size_bytes > MAX_DOCUMENT_SIZE_BYTES:
                    documents_skipped_size += 1
                    continue

                if not document.file_url:
                    documents_failed += 1
                    continue

                documents_downloaded += 1
                supporting_documents.append(document.file_url)

                if live_fetch and agenda_packet_text is None:
                    if "View.ashx?M=A" in document.file_url or "agenda" in document.file_name.lower():
                        extracted = extract_agenda_packet_text(
                            url=document.file_url,
                            timeout_seconds=timeout_seconds,
                            max_retries=max_retries,
                            verify_ssl=verify_ssl,
                        )
                        if extracted:
                            agenda_packet_text = extracted
                            documents_parsed_text_ok += 1

            for agenda_item in agenda_result.agenda_items:
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
                signals_generated += len(signals)
                for signal in signals:
                    if signal.content_available:
                        signals_content_available_count += 1
                    if signal.summary_source == SummarySource.TITLE_ONLY:
                        signals_title_only_count += 1

        documents_parsed_text_empty = max(0, documents_downloaded - documents_parsed_text_ok)
        content_availability_rate = _safe_rate(signals_content_available_count, signals_generated)
        doc_parse_success_rate = _safe_rate(documents_parsed_text_ok, documents_downloaded)
        title_only_rate = _safe_rate(signals_title_only_count, signals_generated)
        connector_failure_count = discovered.metrics.errors_count + documents_failed

        status = _evaluate_status(
            content_availability_rate=content_availability_rate,
            doc_parse_success_rate=doc_parse_success_rate,
            connector_failure_count=connector_failure_count,
        )
        admin_actions = _build_admin_actions(
            signals_title_only_count=signals_title_only_count,
            signals_generated=signals_generated,
        )

        city_summaries.append(
            CityRunHealth(
                city_id=city.city_id,
                platform=city.platform_type.value,
                meetings_discovered=meetings_discovered,
                meetings_processed=meetings_processed,
                agenda_items_processed=agenda_items_processed,
                documents_discovered=documents_discovered,
                documents_downloaded=documents_downloaded,
                documents_failed=documents_failed,
                documents_skipped_size=documents_skipped_size,
                documents_parsed_text_ok=documents_parsed_text_ok,
                documents_parsed_text_empty=documents_parsed_text_empty,
                signals_generated=signals_generated,
                signals_content_available_count=signals_content_available_count,
                signals_title_only_count=signals_title_only_count,
                content_availability_rate=content_availability_rate,
                doc_parse_success_rate=doc_parse_success_rate,
                title_only_rate=title_only_rate,
                status=status,
                admin_actions=admin_actions,
            )
        )

    if not city_summaries:
        totals = _empty_city_record(city_id or "none", "none")
    else:
        totals = CityRunHealth(
            city_id="all",
            platform="all",
            meetings_discovered=sum(item.meetings_discovered for item in city_summaries),
            meetings_processed=sum(item.meetings_processed for item in city_summaries),
            agenda_items_processed=sum(item.agenda_items_processed for item in city_summaries),
            documents_discovered=sum(item.documents_discovered for item in city_summaries),
            documents_downloaded=sum(item.documents_downloaded for item in city_summaries),
            documents_failed=sum(item.documents_failed for item in city_summaries),
            documents_skipped_size=sum(item.documents_skipped_size for item in city_summaries),
            documents_parsed_text_ok=sum(item.documents_parsed_text_ok for item in city_summaries),
            documents_parsed_text_empty=sum(item.documents_parsed_text_empty for item in city_summaries),
            signals_generated=sum(item.signals_generated for item in city_summaries),
            signals_content_available_count=sum(item.signals_content_available_count for item in city_summaries),
            signals_title_only_count=sum(item.signals_title_only_count for item in city_summaries),
            content_availability_rate=_safe_rate(
                sum(item.signals_content_available_count for item in city_summaries),
                sum(item.signals_generated for item in city_summaries),
            ),
            doc_parse_success_rate=_safe_rate(
                sum(item.documents_parsed_text_ok for item in city_summaries),
                sum(item.documents_downloaded for item in city_summaries),
            ),
            title_only_rate=_safe_rate(
                sum(item.signals_title_only_count for item in city_summaries),
                sum(item.signals_generated for item in city_summaries),
            ),
            status=_evaluate_status(
                content_availability_rate=_safe_rate(
                    sum(item.signals_content_available_count for item in city_summaries),
                    sum(item.signals_generated for item in city_summaries),
                ),
                doc_parse_success_rate=_safe_rate(
                    sum(item.documents_parsed_text_ok for item in city_summaries),
                    sum(item.documents_downloaded for item in city_summaries),
                ),
                connector_failure_count=sum(item.documents_failed for item in city_summaries),
            ),
            admin_actions=_build_admin_actions(
                signals_title_only_count=sum(item.signals_title_only_count for item in city_summaries),
                signals_generated=sum(item.signals_generated for item in city_summaries),
            ),
        )

    return RunHealthSummary(cities=city_summaries, totals=totals)
