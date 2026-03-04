from __future__ import annotations

from dataclasses import dataclass

from .city_registry import phase1_city_registry
from .connectors.contracts import validate_discover_result
from .connectors.errors import ConnectorContractError
from .connectors.errors import UnsupportedPlatformError
from .connectors.models import ConnectorError, ConnectorRequest, DateRange
from .connectors.registry import ConnectorRegistry


@dataclass(frozen=True)
class AgendaItemDebugSample:
    item_number: str
    title: str
    has_description: bool
    attachments_count: int


@dataclass(frozen=True)
class MeetingDebugRecord:
    meeting_id: str
    meeting_detail_url: str
    meeting_detail_http_status: int
    agenda_items_count: int
    sample_items: tuple[AgendaItemDebugSample, ...]


@dataclass(frozen=True)
class HarnessResult:
    city_id: str
    platform: str
    status: str
    meetings_discovered: int
    meetings_parsed: int
    meeting_detail_200_count: int
    agenda_items_extracted: int
    documents_discovered: int
    live_fetch_requested: bool
    fallback_count: int
    meeting_debug: tuple[MeetingDebugRecord, ...]
    errors: tuple[ConnectorError, ...]


def run_connector_dry_harness(
    start_date: str,
    end_date: str,
    city_id: str | None = None,
    live_fetch: bool = False,
    timeout_seconds: int = 20,
    max_retries: int = 2,
    verify_ssl: bool = True,
    debug_meetings: bool = False,
) -> list[HarnessResult]:
    registry = ConnectorRegistry.with_defaults()
    results: list[HarnessResult] = []

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
            debug_meetings=debug_meetings,
        )

        try:
            connector = registry.resolve(city.platform_type)
            discovered = connector.discover_meetings(request)
            validate_discover_result(city.platform_type, discovered)

            meetings_parsed = 0
            meeting_detail_200_count = 0
            agenda_items_extracted = 0
            documents_discovered = 0
            meeting_debug: list[MeetingDebugRecord] = []

            if debug_meetings:
                for meeting in discovered.meetings:
                    agenda_result = connector.parse_agenda(request, meeting)
                    document_result = connector.extract_documents(request, meeting)
                    meetings_parsed += agenda_result.metrics.meetings_parsed or 1
                    meeting_detail_200_count += agenda_result.metrics.meeting_detail_200_count
                    agenda_items_extracted += len(agenda_result.agenda_items)
                    documents_discovered += len(document_result.documents)

                    sample_items = tuple(
                        AgendaItemDebugSample(
                            item_number=item.item_number,
                            title=item.title,
                            has_description=bool(item.summary and item.summary.strip()),
                            attachments_count=0,
                        )
                        for item in agenda_result.agenda_items[:3]
                    )
                    meeting_debug.append(
                        MeetingDebugRecord(
                            meeting_id=meeting.external_meeting_id,
                            meeting_detail_url=meeting.source_url,
                            meeting_detail_http_status=200 if agenda_result.metrics.meeting_detail_200_count > 0 else 0,
                            agenda_items_count=len(agenda_result.agenda_items),
                            sample_items=sample_items,
                        )
                    )

            results.append(
                HarnessResult(
                    city_id=city.city_id,
                    platform=city.platform_type.value,
                    status="degraded" if discovered.metrics.errors_count > 0 else "ok",
                    meetings_discovered=discovered.metrics.meetings_discovered,
                    meetings_parsed=meetings_parsed,
                    meeting_detail_200_count=meeting_detail_200_count,
                    agenda_items_extracted=agenda_items_extracted,
                    documents_discovered=documents_discovered,
                    live_fetch_requested=live_fetch,
                    fallback_count=discovered.metrics.errors_count,
                    meeting_debug=tuple(meeting_debug),
                    errors=(),
                )
            )
        except ConnectorContractError as error:
            results.append(
                HarnessResult(
                    city_id=city.city_id,
                    platform=city.platform_type.value,
                    status="error",
                    meetings_discovered=0,
                    meetings_parsed=0,
                    meeting_detail_200_count=0,
                    agenda_items_extracted=0,
                    documents_discovered=0,
                    live_fetch_requested=live_fetch,
                    fallback_count=0,
                    meeting_debug=(),
                    errors=(
                        ConnectorError(
                            error_code="connector_contract_error",
                            platform_type=city.platform_type,
                            city_id=city.city_id,
                            body_name=",".join(city.bodies),
                            source_url=city.discovery_url,
                            message=str(error),
                            retryable=False,
                        ),
                    ),
                )
            )
        except UnsupportedPlatformError:
            results.append(
                HarnessResult(
                    city_id=city.city_id,
                    platform=str(city.platform_type),
                    status="error",
                    meetings_discovered=0,
                    meetings_parsed=0,
                    meeting_detail_200_count=0,
                    agenda_items_extracted=0,
                    documents_discovered=0,
                    live_fetch_requested=live_fetch,
                    fallback_count=0,
                    meeting_debug=(),
                    errors=(
                        ConnectorError(
                            error_code="unsupported_platform",
                            platform_type=city.platform_type,
                            city_id=city.city_id,
                            body_name=",".join(city.bodies),
                            source_url=city.discovery_url,
                            message="Unsupported platform for city",
                            retryable=False,
                        ),
                    ),
                )
            )

    return results
