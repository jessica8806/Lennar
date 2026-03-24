import unittest
from unittest.mock import patch

from civicsignal.city_registry import CityConfig
from civicsignal.connectors.models import (
    AgendaItemRecord,
    ConnectorRequest,
    DiscoverMeetingsResult,
    DocumentRecord,
    DocumentType,
    DryRunMetrics,
    ExtractDocumentsResult,
    MeetingRecord,
    ParseAgendaResult,
    PlatformType,
)
from civicsignal.system_health import run_system_health


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


class SystemHealthTests(unittest.TestCase):
    def test_city_health_contains_required_metrics(self) -> None:
        summary = run_system_health(
            start_date="2026-03-01",
            end_date="2026-03-31",
            city_id="fullerton",
            live_fetch=False,
        )

        self.assertEqual(len(summary.cities), 1)
        city = summary.cities[0]
        self.assertEqual(city.city_id, "fullerton")
        self.assertGreaterEqual(city.meetings_discovered, 1)
        self.assertGreaterEqual(city.agenda_items_processed, 1)
        self.assertGreaterEqual(city.documents_discovered, 1)
        self.assertGreaterEqual(city.signals_generated, 1)
        self.assertGreaterEqual(city.signals_title_only_count, 1)
        self.assertIn(city.status, {"healthy", "warning", "failed"})

    def test_title_only_admin_prompt_is_emitted(self) -> None:
        summary = run_system_health(
            start_date="2026-03-01",
            end_date="2026-03-31",
            city_id="fullerton",
            live_fetch=False,
        )
        city = summary.cities[0]
        self.assertTrue(any("title-only" in action for action in city.admin_actions))

    def test_totals_roll_up(self) -> None:
        summary = run_system_health(
            start_date="2026-03-01",
            end_date="2026-03-31",
            city_id="fullerton",
            live_fetch=False,
        )
        city = summary.cities[0]
        self.assertEqual(summary.totals.signals_generated, city.signals_generated)
        self.assertEqual(summary.totals.documents_discovered, city.documents_discovered)

    @patch("civicsignal.system_health.extract_agenda_packet_text")
    @patch("civicsignal.system_health.ConnectorRegistry.with_defaults")
    @patch("civicsignal.system_health.phase1_city_registry")
    def test_health_counts_extracted_document_text_when_available(
        self,
        mock_city_registry,
        mock_registry_defaults,
        mock_extract_text,
    ) -> None:
        mock_extract_text.return_value = (
            "Agenda packet narrative contains zoning and contract details for municipal action."
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

        summary = run_system_health(
            start_date="2026-03-01",
            end_date="2026-03-03",
            city_id="test-city",
            live_fetch=True,
        )

        self.assertEqual(len(summary.cities), 1)
        city = summary.cities[0]
        self.assertGreaterEqual(city.documents_parsed_text_ok, 1)
        self.assertGreaterEqual(city.signals_content_available_count, 1)


if __name__ == "__main__":
    unittest.main()
