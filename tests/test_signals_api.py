import unittest

from civicsignal.signals_api import get_signal, list_signals


class SignalsApiTests(unittest.TestCase):
    def test_list_signals_returns_paginated_payload(self) -> None:
        response = list_signals(
            start_date="2026-03-01",
            end_date="2026-03-03",
            city="fullerton",
            limit=5,
            offset=0,
        )

        self.assertGreaterEqual(response.total, 1)
        self.assertGreaterEqual(len(response.items), 1)
        self.assertEqual(response.limit, 5)
        self.assertEqual(response.offset, 0)

    def test_list_signals_filters_content_available(self) -> None:
        response = list_signals(
            start_date="2026-03-01",
            end_date="2026-03-03",
            city="fullerton",
            content_available="false",
        )

        self.assertGreaterEqual(response.total, 1)
        self.assertTrue(all(not signal.content_available for signal in response.items))

    def test_list_signals_sorts_by_confidence(self) -> None:
        response = list_signals(
            start_date="2026-03-01",
            end_date="2026-03-03",
            city="fullerton",
            sort_by="confidence",
            sort_order="desc",
        )

        confidences = [signal.confidence.value for signal in response.items]
        ranks = {"High": 3, "Medium": 2, "Low": 1}
        numeric = [ranks[value] for value in confidences]
        self.assertEqual(numeric, sorted(numeric, reverse=True))

    def test_get_signal_returns_detail(self) -> None:
        list_response = list_signals(
            start_date="2026-03-01",
            end_date="2026-03-03",
            city="fullerton",
            limit=1,
        )

        signal = get_signal(
            signal_id=list_response.items[0].signal_id,
            start_date="2026-03-01",
            end_date="2026-03-03",
        )

        self.assertEqual(signal.signal_id, list_response.items[0].signal_id)
        self.assertTrue(signal.source_urls)

    def test_get_signal_raises_for_unknown_id(self) -> None:
        with self.assertRaises(KeyError):
            get_signal(
                signal_id="missing-signal-id",
                start_date="2026-03-01",
                end_date="2026-03-03",
            )


if __name__ == "__main__":
    unittest.main()
