import unittest

from civicsignal.scheduler import run_dry_scheduler


class SchedulerDryRunTests(unittest.TestCase):
    def test_dry_run_invokes_all_phase1_cities(self) -> None:
        logs = run_dry_scheduler(start_date="2026-03-01", end_date="2026-03-03")

        self.assertEqual(len(logs), 10)
        self.assertTrue(all(log.meetings_discovered >= 2 for log in logs))
        self.assertTrue(all(len(log.bodies) == 2 for log in logs))

        city_ids = {log.city_id for log in logs}
        expected = {
            "irvine",
            "anaheim",
            "santa-ana",
            "huntington-beach",
            "newport-beach",
            "costa-mesa",
            "fullerton",
            "garden-grove",
            "mission-viejo",
            "laguna-niguel",
        }
        self.assertSetEqual(city_ids, expected)


if __name__ == "__main__":
    unittest.main()
