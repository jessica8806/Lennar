import unittest

from civicsignal.search_service import search_index


class SearchServiceTests(unittest.TestCase):
    def test_search_returns_grouped_entities(self) -> None:
        response = search_index(
            start_date="2026-03-01",
            end_date="2026-03-03",
            query="planning",
            city="fullerton",
            live_fetch=False,
        )

        self.assertGreaterEqual(len(response.signals), 1)
        self.assertGreaterEqual(len(response.projects), 1)
        self.assertGreaterEqual(len(response.meetings), 1)
        self.assertGreaterEqual(len(response.documents), 1)

    def test_search_filters_by_meeting_body(self) -> None:
        response = search_index(
            start_date="2026-03-01",
            end_date="2026-03-03",
            query="",
            city="fullerton",
            meeting_body="Planning Commission",
            live_fetch=False,
        )

        self.assertGreaterEqual(len(response.signals), 1)
        self.assertTrue(all("planning commission" in row.meeting_body.lower() for row in response.signals))


if __name__ == "__main__":
    unittest.main()
