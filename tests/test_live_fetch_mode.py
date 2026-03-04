import unittest
from unittest.mock import patch

from civicsignal.connectors.fetch import FetchResult
from civicsignal.connectors.models import ConnectorRequest, DateRange, PlatformType
from civicsignal.connectors.stub import GranicusConnector, LegistarConnector


class LiveFetchModeTests(unittest.TestCase):
    @patch("civicsignal.connectors.stub.fetch_html_with_fallback")
    def test_granicus_live_fetch_fallback_counts_error(self, mock_fetch) -> None:
        mock_fetch.return_value = FetchResult(html="<html></html>", used_live_source=False, fallback_reason="timeout")
        connector = GranicusConnector()
        request = ConnectorRequest(
            city_id="irvine",
            city_name="Irvine",
            platform_type=PlatformType.GRANICUS,
            discovery_url="https://irvine.granicus.com/ViewPublisher.php",
            bodies=["City Council", "Planning Commission"],
            date_range=DateRange(start_date="2026-03-01", end_date="2026-03-03"),
            dry_run=True,
            live_fetch=True,
        )

        result = connector.discover_meetings(request)
        self.assertEqual(len(result.meetings), 2)
        self.assertGreaterEqual(result.metrics.errors_count, 1)

    @patch("civicsignal.connectors.stub.fetch_html_with_fallback")
    def test_legistar_live_fetch_empty_parse_uses_sample_fallback(self, mock_fetch) -> None:
        mock_fetch.return_value = FetchResult(html="<html><body>No rows</body></html>", used_live_source=True)
        connector = LegistarConnector()
        request = ConnectorRequest(
            city_id="huntington-beach",
            city_name="Huntington Beach",
            platform_type=PlatformType.LEGISTAR,
            discovery_url="https://huntingtonbeach.legistar.com/Calendar.aspx",
            bodies=["City Council", "Planning Commission"],
            date_range=DateRange(start_date="2026-03-01", end_date="2026-03-03"),
            dry_run=True,
            live_fetch=True,
        )

        result = connector.discover_meetings(request)
        self.assertEqual(len(result.meetings), 2)
        self.assertGreaterEqual(result.metrics.errors_count, 1)

    @patch("civicsignal.connectors.stub.fetch_html_with_fallback")
    def test_legistar_live_fetch_failure_does_not_emit_stub_meetings(self, mock_fetch) -> None:
        mock_fetch.return_value = FetchResult(html="<html></html>", used_live_source=False, fallback_reason="timeout")
        connector = LegistarConnector()
        request = ConnectorRequest(
            city_id="costa-mesa",
            city_name="Costa Mesa",
            platform_type=PlatformType.LEGISTAR,
            discovery_url="https://costamesa.legistar.com/Calendar.aspx",
            bodies=["City Council", "Planning Commission"],
            date_range=DateRange(start_date="2026-03-01", end_date="2026-03-03"),
            dry_run=True,
            live_fetch=True,
        )

        result = connector.discover_meetings(request)
        self.assertEqual(len(result.meetings), 0)
        self.assertGreaterEqual(result.metrics.errors_count, 1)


if __name__ == "__main__":
    unittest.main()
