from __future__ import annotations

from dataclasses import dataclass

from .models import PlatformType


@dataclass(frozen=True)
class UnsupportedPlatformError(Exception):
    platform_type: str

    @property
    def code(self) -> str:
        return "unsupported_platform"

    def __str__(self) -> str:
        return f"Unsupported platform '{self.platform_type}'. Configure a valid connector adapter."


@dataclass(frozen=True)
class ConnectorContractError(Exception):
    platform_type: PlatformType
    message: str

    def __str__(self) -> str:
        return f"Connector contract error ({self.platform_type.value}): {self.message}"
