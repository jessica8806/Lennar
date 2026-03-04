from __future__ import annotations

from dataclasses import dataclass

from .errors import UnsupportedPlatformError
from .interface import PlatformConnector
from .models import PlatformType
from .stub import (
    CivicPlusConnector,
    GranicusConnector,
    LaserficheConnector,
    LegistarConnector,
    NovusAgendaConnector,
    OnBaseConnector,
)


@dataclass
class ConnectorRegistry:
    _connectors: dict[PlatformType, PlatformConnector]

    @classmethod
    def with_defaults(cls) -> "ConnectorRegistry":
        return cls(
            _connectors={
                PlatformType.GRANICUS: GranicusConnector(),
                PlatformType.LEGISTAR: LegistarConnector(),
                PlatformType.LASERFICHE: LaserficheConnector(),
                PlatformType.NOVUSAGENDA: NovusAgendaConnector(),
                PlatformType.ONBASE: OnBaseConnector(),
                PlatformType.CIVICPLUS: CivicPlusConnector(),
            }
        )

    def resolve(self, platform_type: PlatformType | str) -> PlatformConnector:
        if isinstance(platform_type, str):
            normalized = platform_type.strip().lower()
            try:
                platform_enum = PlatformType(normalized)
            except ValueError as error:
                raise UnsupportedPlatformError(platform_type=platform_type) from error
        else:
            platform_enum = platform_type

        connector = self._connectors.get(platform_enum)
        if connector is None:
            raise UnsupportedPlatformError(platform_type=platform_enum.value)
        return connector
