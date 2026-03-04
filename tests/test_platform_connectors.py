import unittest

from civicsignal.connectors.models import ConnectorRequest, DateRange, PlatformType
from civicsignal.connectors.stub import GranicusConnector, LegistarConnector


class PlatformConnectorTests(unittest.TestCase):
    def test_granicus_discovery_filters_to_requested_bodies(self) -> None:
        connector = GranicusConnector()
        request = ConnectorRequest(
            city_id="irvine",
            city_name="Irvine",
            platform_type=PlatformType.GRANICUS,
            discovery_url="https://irvine.granicus.com/ViewPublisher.php",
            bodies=["City Council"],
            date_range=DateRange(start_date="2026-03-01", end_date="2026-03-03"),
            dry_run=True,
        )

        result = connector.discover_meetings(request)
        self.assertEqual(len(result.meetings), 1)
        self.assertEqual(result.meetings[0].meeting_body, "City Council")
        self.assertGreaterEqual(result.metrics.meetings_discovered, 1)

    def test_legistar_discovery_returns_expected_links(self) -> None:
        connector = LegistarConnector()
        request = ConnectorRequest(
            city_id="huntington-beach",
            city_name="Huntington Beach",
            platform_type=PlatformType.LEGISTAR,
            discovery_url="https://huntingtonbeach.legistar.com/Calendar.aspx",
            bodies=["City Council", "Planning Commission"],
            date_range=DateRange(start_date="2026-03-01", end_date="2026-03-03"),
            dry_run=True,
        )

        result = connector.discover_meetings(request)
        self.assertEqual(len(result.meetings), 2)
        self.assertTrue(all(meeting.agenda_url for meeting in result.meetings))
        self.assertTrue(all(meeting.minutes_url for meeting in result.meetings))

    def test_legistar_documents_use_view_ashx_links(self) -> None:
        connector = LegistarConnector()
        request = ConnectorRequest(
            city_id="fullerton",
            city_name="Fullerton",
            platform_type=PlatformType.LEGISTAR,
            discovery_url="https://fullerton.legistar.com/Calendar.aspx",
            bodies=["City Council", "Planning Commission"],
            date_range=DateRange(start_date="2026-03-01", end_date="2026-03-31"),
            dry_run=True,
        )

        result = connector.discover_meetings(request)
        self.assertGreaterEqual(len(result.meetings), 1)
        documents = connector.extract_documents(request, result.meetings[0]).documents
        self.assertGreaterEqual(len(documents), 1)
        self.assertTrue(any("View.ashx" in document.file_url for document in documents))
        self.assertTrue(all("MeetingDetail.aspx" not in document.file_url or "View.ashx" in document.file_url for document in documents))

    def test_legistar_parse_agenda_extracts_multiple_items(self) -> None:
        connector = LegistarConnector()
        request = ConnectorRequest(
            city_id="costa-mesa",
            city_name="Costa Mesa",
            platform_type=PlatformType.LEGISTAR,
            discovery_url="https://costamesa.legistar.com/Calendar.aspx",
            bodies=["City Council", "Planning Commission"],
            date_range=DateRange(start_date="2026-03-01", end_date="2026-03-31"),
            dry_run=True,
        )

        discovered = connector.discover_meetings(request)
        self.assertGreaterEqual(len(discovered.meetings), 1)
        parsed = connector.parse_agenda(request, discovered.meetings[0])

        self.assertGreaterEqual(len(parsed.agenda_items), 10)
        self.assertNotEqual({item.item_number for item in parsed.agenda_items}, {"1"})


if __name__ == "__main__":
    unittest.main()
