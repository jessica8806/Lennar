from __future__ import annotations

from .errors import ConnectorContractError
from .models import (
    MAX_DOCUMENT_SIZE_BYTES,
    DiscoverMeetingsResult,
    ExtractDocumentsResult,
    PlatformType,
)


def validate_discover_result(platform: PlatformType, result: DiscoverMeetingsResult) -> None:
    for meeting in result.meetings:
        if not meeting.external_meeting_id:
            raise ConnectorContractError(platform, "missing external_meeting_id")
        if not meeting.meeting_date:
            raise ConnectorContractError(platform, "missing meeting_date")
        if not meeting.meeting_title:
            raise ConnectorContractError(platform, "missing meeting_title")
        if not meeting.meeting_body:
            raise ConnectorContractError(platform, "missing meeting_body")
        if not meeting.source_url:
            raise ConnectorContractError(platform, "missing source_url")


def validate_documents_result(platform: PlatformType, result: ExtractDocumentsResult) -> None:
    for document in result.documents:
        if not document.external_document_id:
            raise ConnectorContractError(platform, "missing external_document_id")
        if not document.file_url:
            raise ConnectorContractError(platform, "missing file_url")
        if document.file_size_bytes > MAX_DOCUMENT_SIZE_BYTES:
            raise ConnectorContractError(
                platform,
                f"document exceeds max size {MAX_DOCUMENT_SIZE_BYTES} bytes: {document.file_name}",
            )
