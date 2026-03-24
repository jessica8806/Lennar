import unittest

from civicsignal.connectors.contracts import validate_discover_result, validate_documents_result
from civicsignal.connectors.errors import ConnectorContractError
from civicsignal.connectors.models import (
    DiscoverMeetingsResult,
    DocumentRecord,
    DocumentType,
    DryRunMetrics,
    ExtractDocumentsResult,
    MeetingRecord,
    PlatformType,
)


class ConnectorContractTests(unittest.TestCase):
    def test_discover_result_requires_source_url(self) -> None:
        result = DiscoverMeetingsResult(
            meetings=[
                MeetingRecord(
                    external_meeting_id="m-1",
                    meeting_date="2026-03-03",
                    meeting_title="City Council",
                    meeting_body="City Council",
                    agenda_url=None,
                    minutes_url=None,
                    video_url=None,
                    source_url="",
                )
            ],
            metrics=DryRunMetrics(meetings_discovered=1),
        )

        with self.assertRaises(ConnectorContractError):
            validate_discover_result(PlatformType.GRANICUS, result)

    def test_document_size_limit_enforced(self) -> None:
        result = ExtractDocumentsResult(
            documents=[
                DocumentRecord(
                    external_document_id="d-1",
                    document_type=DocumentType.AGENDA_PACKET,
                    file_url="https://example.com/agenda_packet.pdf",
                    file_name="agenda_packet.pdf",
                    file_size_bytes=26 * 1024 * 1024,
                )
            ]
        )

        with self.assertRaises(ConnectorContractError):
            validate_documents_result(PlatformType.LEGISTAR, result)


if __name__ == "__main__":
    unittest.main()
