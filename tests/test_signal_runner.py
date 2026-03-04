import unittest
from unittest.mock import patch

from civicsignal.city_registry import CityConfig
from civicsignal.connectors.models import (
    AgendaItemRecord,
    ConnectorRequest,
    DateRange,
    DiscoverMeetingsResult,
    DocumentRecord,
    DocumentType,
    DryRunMetrics,
    ExtractDocumentsResult,
    MeetingRecord,
    ParseAgendaResult,
    PlatformType,
)
from civicsignal.signal_runner import run_signal_generation


class _FakeConnector:
    def discover_meetings(self, request: ConnectorRequest) -> DiscoverMeetingsResult:
        return DiscoverMeetingsResult(
            meetings=[
                MeetingRecord(
                    external_meeting_id="meeting-1",
                    meeting_date="2026-03-01",
                    meeting_title="City Council Meeting",
                    meeting_body="City Council",
                    agenda_url="https://example.com/MeetingDetail.aspx?ID=12345",
                    minutes_url=None,
                    video_url=None,
                    source_url="https://example.com/MeetingDetail.aspx?ID=12345",
                )
            ],
            metrics=DryRunMetrics(meetings_discovered=1),
        )

    def parse_agenda(self, request: ConnectorRequest, meeting: MeetingRecord) -> ParseAgendaResult:
        return ParseAgendaResult(
            agenda_items=[
                AgendaItemRecord(
                    external_agenda_item_id="agenda-1",
                    item_number="1",
                    title="Contract award and ordinance update",
                    summary=None,
                    action=None,
                    vote_result=None,
                )
            ],
            metrics=DryRunMetrics(agenda_items_parsed=1),
        )

    def extract_documents(self, request: ConnectorRequest, meeting: MeetingRecord) -> ExtractDocumentsResult:
        return ExtractDocumentsResult(
            documents=[
                DocumentRecord(
                    external_document_id="doc-1",
                    document_type=DocumentType.AGENDA,
                    file_url="https://example.com/View.ashx?M=A&ID=12345",
                    file_name="agenda_packet.pdf",
                    file_size_bytes=1024,
                )
            ],
            metrics=DryRunMetrics(documents_referenced=1),
        )


class _FakeRegistry:
    def resolve(self, platform_type: PlatformType) -> _FakeConnector:
        return _FakeConnector()


class SignalRunnerTests(unittest.TestCase):
    def test_signal_runner_generates_signals_for_city(self) -> None:
        summaries, signals = run_signal_generation(
            start_date="2026-03-01",
            end_date="2026-03-03",
            city_id="fullerton",
            live_fetch=False,
        )

        self.assertEqual(len(summaries), 1)
        self.assertGreaterEqual(summaries[0].meetings_processed, 1)
        self.assertGreaterEqual(summaries[0].agenda_items_processed, 1)
        self.assertGreaterEqual(summaries[0].signals_generated, 1)
        self.assertEqual(summaries[0].signals_generated, len(signals))

    @patch("civicsignal.signal_runner.extract_agenda_packet_text")
    @patch("civicsignal.signal_runner.ConnectorRegistry.with_defaults")
    @patch("civicsignal.signal_runner.phase1_city_registry")
    def test_signal_runner_uses_agenda_packet_text_when_available(
        self,
        mock_city_registry,
        mock_registry_defaults,
        mock_extract_text,
    ) -> None:
        mock_extract_text.return_value = (
            "This staff report supports contract award approval and ordinance adoption for a city project."
        )
        mock_city_registry.return_value = [
            CityConfig(
                city_id="test-city",
                city_name="Test City",
                platform_type=PlatformType.LEGISTAR,
                discovery_url="https://example.com/Calendar.aspx",
                bodies=["City Council"],
            )
        ]
        mock_registry_defaults.return_value = _FakeRegistry()

        summaries, signals = run_signal_generation(
            start_date="2026-03-01",
            end_date="2026-03-03",
            city_id="test-city",
            live_fetch=True,
        )

        self.assertEqual(len(summaries), 1)
        self.assertGreaterEqual(len(signals), 1)
        self.assertTrue(any(signal.content_available for signal in signals))
        self.assertTrue(any(signal.summary_source.value == "agenda_packet" for signal in signals))


if __name__ == "__main__":
    unittest.main()
