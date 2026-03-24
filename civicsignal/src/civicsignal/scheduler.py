from __future__ import annotations

from dataclasses import dataclass

from .city_registry import CityConfig, phase1_city_registry
from .connectors.contracts import validate_discover_result
from .connectors.models import ConnectorRequest, DateRange
from .connectors.registry import ConnectorRegistry


@dataclass(frozen=True)
class DryRunLog:
    city_id: str
    platform: str
    bodies: list[str]
    meetings_discovered: int
    live_fetch_requested: bool
    fallback_count: int


def run_dry_scheduler(
    start_date: str,
    end_date: str,
    live_fetch: bool = False,
    timeout_seconds: int = 20,
    max_retries: int = 2,
    verify_ssl: bool = True,
) -> list[DryRunLog]:
    registry = ConnectorRegistry.with_defaults()
    logs: list[DryRunLog] = []

    for city in phase1_city_registry():
        request = _to_request(
            city,
            start_date=start_date,
            end_date=end_date,
            live_fetch=live_fetch,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            verify_ssl=verify_ssl,
        )
        connector = registry.resolve(city.platform_type)
        discovered = connector.discover_meetings(request)
        validate_discover_result(city.platform_type, discovered)
        logs.append(
            DryRunLog(
                city_id=city.city_id,
                platform=city.platform_type.value,
                bodies=city.bodies,
                meetings_discovered=discovered.metrics.meetings_discovered,
                live_fetch_requested=live_fetch,
                fallback_count=discovered.metrics.errors_count,
            )
        )

    return logs


def _to_request(
    city: CityConfig,
    start_date: str,
    end_date: str,
    live_fetch: bool,
    timeout_seconds: int,
    max_retries: int,
    verify_ssl: bool,
) -> ConnectorRequest:
    return ConnectorRequest(
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
