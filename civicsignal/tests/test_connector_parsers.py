import unittest
from pathlib import Path

from civicsignal.connectors.parsers import parse_granicus_meetings, parse_legistar_agenda_items, parse_legistar_meetings

FIXTURE_DIR = Path(__file__).parent / "fixtures"


class ConnectorParserTests(unittest.TestCase):
    def test_parse_granicus_fixture(self) -> None:
        html = (FIXTURE_DIR / "granicus_calendar.html").read_text(encoding="utf-8")
        meetings = parse_granicus_meetings(html, city_id="irvine")

        self.assertEqual(len(meetings), 2)
        self.assertEqual(meetings[0].meeting_body, "City Council")
        self.assertEqual(meetings[1].meeting_body, "Planning Commission")
        self.assertTrue(meetings[0].agenda_url)
        self.assertTrue(meetings[0].external_meeting_id.startswith("irvine-"))

    def test_parse_legistar_fixture(self) -> None:
        html = (FIXTURE_DIR / "legistar_calendar.html").read_text(encoding="utf-8")
        meetings = parse_legistar_meetings(
            html,
            city_id="huntington-beach",
            base_url="https://huntingtonbeach.legistar.com/Calendar.aspx",
        )

        self.assertEqual(len(meetings), 2)
        self.assertEqual(meetings[0].meeting_body, "City Council")
        self.assertEqual(meetings[1].meeting_body, "Planning Commission")
        self.assertTrue(meetings[1].minutes_url)
        self.assertTrue(meetings[0].external_meeting_id.startswith("huntington-beach-"))

    def test_parse_legistar_telerik_fixture(self) -> None:
        html = (FIXTURE_DIR / "legistar_telerik_calendar.html").read_text(encoding="utf-8")
        meetings = parse_legistar_meetings(
            html,
            city_id="fullerton",
            base_url="https://fullerton.legistar.com/Calendar.aspx",
        )

        self.assertEqual(len(meetings), 2)
        self.assertIn("City Council", meetings[0].meeting_body)
        self.assertEqual(meetings[0].meeting_date, "03/12/2026")
        self.assertTrue(meetings[0].agenda_url.startswith("https://fullerton.legistar.com/"))
        self.assertTrue(meetings[0].source_url.startswith("https://fullerton.legistar.com/"))

        def test_parse_legistar_agenda_items_fixture_shape(self) -> None:
                html = """
                <table id=\"ctl00_ContentPlaceHolder1_gridAgenda_ctl00\">
                    <tr id=\"ctl00_ContentPlaceHolder1_gridAgenda_ctl00__0\">
                        <td>1</td><td><a>Public hearing for zoning amendment</a></td><td>Consider ordinance text</td>
                    </tr>
                    <tr id=\"ctl00_ContentPlaceHolder1_gridAgenda_ctl00__1\">
                        <td>2</td><td><a>Contract award for utility repairs</a></td><td>Approve vendor agreement</td>
                    </tr>
                    <tr id=\"ctl00_ContentPlaceHolder1_gridAgenda_ctl00__2\">
                        <td>3</td><td><a>Capital improvement budget update</a></td><td>Adopt CIP revisions</td>
                    </tr>
                </table>
                """
                items = parse_legistar_agenda_items(html, city_id="costa-mesa", meeting_external_id="costa-123")
                self.assertEqual(len(items), 3)
                self.assertEqual(items[0].item_number, "1")
                self.assertIn("zoning", items[0].title.lower())
                self.assertTrue(items[0].summary)


if __name__ == "__main__":
    unittest.main()
