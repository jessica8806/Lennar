from __future__ import annotations

from abc import ABC, abstractmethod

from .models import (
    ConnectorRequest,
    DiscoverMeetingsResult,
    ExtractDocumentsResult,
    MeetingRecord,
    ParseAgendaResult,
)


class PlatformConnector(ABC):
    platform_name: str

    @abstractmethod
    def discover_meetings(self, request: ConnectorRequest) -> DiscoverMeetingsResult:
        raise NotImplementedError

    @abstractmethod
    def parse_agenda(self, request: ConnectorRequest, meeting: MeetingRecord) -> ParseAgendaResult:
        raise NotImplementedError

    @abstractmethod
    def extract_documents(self, request: ConnectorRequest, meeting: MeetingRecord) -> ExtractDocumentsResult:
        raise NotImplementedError
