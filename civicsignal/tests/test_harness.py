import unittest

from civicsignal.harness import run_connector_dry_harness


class HarnessTests(unittest.TestCase):
    def test_harness_runs_all_cities(self) -> None:
        results = run_connector_dry_harness(start_date="2026-03-01", end_date="2026-03-03")
        self.assertEqual(len(results), 10)
        self.assertTrue(all(result.status == "ok" for result in results))

    def test_harness_city_filter(self) -> None:
        results = run_connector_dry_harness(
            start_date="2026-03-01",
            end_date="2026-03-03",
            city_id="irvine",
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].city_id, "irvine")

    def test_harness_debug_meetings_includes_diagnostics(self) -> None:
        results = run_connector_dry_harness(
            start_date="2026-03-01",
            end_date="2026-03-31",
            city_id="costa-mesa",
            debug_meetings=True,
        )
        self.assertEqual(len(results), 1)
        self.assertGreaterEqual(results[0].meetings_discovered, 1)
        self.assertGreaterEqual(results[0].meetings_parsed, 1)
        self.assertGreaterEqual(results[0].agenda_items_extracted, 10)
        self.assertGreaterEqual(len(results[0].meeting_debug), 1)


if __name__ == "__main__":
    unittest.main()
