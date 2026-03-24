import json
import threading
import unittest
import urllib.request

from civicsignal.api_server import SignalsApiServerConfig, create_signals_api_server


class SignalsHttpApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = create_signals_api_server(
            host="127.0.0.1",
            port=0,
            config=SignalsApiServerConfig(
                start_date="2026-03-01",
                end_date="2026-03-03",
                city="fullerton",
                live_fetch=False,
            ),
        )
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def _get_json(self, path: str) -> tuple[int, dict]:
        url = f"http://127.0.0.1:{self.port}{path}"
        try:
            with urllib.request.urlopen(url, timeout=20) as response:
                body = response.read().decode("utf-8")
                return response.status, json.loads(body)
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8")
            return error.code, json.loads(body)

    def test_signals_list_endpoint_returns_items(self) -> None:
        status, payload = self._get_json("/signals?limit=2")
        self.assertEqual(status, 200)
        self.assertIn("items", payload)
        self.assertIn("total", payload)
        self.assertLessEqual(len(payload["items"]), 2)

    def test_signals_detail_endpoint_returns_record(self) -> None:
        _, list_payload = self._get_json("/signals?limit=1")
        signal_id = list_payload["items"][0]["signal_id"]

        status, detail = self._get_json(f"/signals/{signal_id}")
        self.assertEqual(status, 200)
        self.assertEqual(detail["signal_id"], signal_id)

    def test_signals_detail_returns_404_for_unknown_id(self) -> None:
        status, payload = self._get_json("/signals/does-not-exist")
        self.assertEqual(status, 404)
        self.assertIn("error", payload)

    def test_signals_list_returns_400_for_invalid_limit(self) -> None:
        status, payload = self._get_json("/signals?limit=0")
        self.assertEqual(status, 400)
        self.assertIn("error", payload)

    def test_projects_list_endpoint_returns_items(self) -> None:
        status, payload = self._get_json("/projects?limit=2")
        self.assertEqual(status, 200)
        self.assertIn("items", payload)
        self.assertIn("total", payload)
        self.assertLessEqual(len(payload["items"]), 2)

    def test_projects_detail_endpoint_returns_record(self) -> None:
        _, list_payload = self._get_json("/projects?limit=1")
        project_id = list_payload["items"][0]["project_id"]

        status, detail = self._get_json(f"/projects/{project_id}")
        self.assertEqual(status, 200)
        self.assertEqual(detail["project_id"], project_id)

    def test_projects_detail_returns_404_for_unknown_id(self) -> None:
        status, payload = self._get_json("/projects/does-not-exist")
        self.assertEqual(status, 404)
        self.assertIn("error", payload)

    def test_search_endpoint_returns_grouped_results(self) -> None:
        status, payload = self._get_json("/search?q=planning")
        self.assertEqual(status, 200)
        self.assertIn("signals", payload)
        self.assertIn("projects", payload)
        self.assertIn("meetings", payload)
        self.assertIn("documents", payload)

    def test_dashboard_endpoint_returns_html_with_required_sections(self) -> None:
        url = f"http://127.0.0.1:{self.port}/dashboard"
        with urllib.request.urlopen(url, timeout=20) as response:
            html = response.read().decode("utf-8")
            status = response.status

        self.assertEqual(status, 200)
        self.assertIn("New Signals (24h)", html)
        self.assertIn("Signals by Category", html)
        self.assertIn("Signals by City", html)
        self.assertIn("Trending Projects", html)
        self.assertIn("Signals Table", html)
        self.assertIn("badge-title_only", html)
        self.assertIn("f-confidence", html)


if __name__ == "__main__":
    unittest.main()
