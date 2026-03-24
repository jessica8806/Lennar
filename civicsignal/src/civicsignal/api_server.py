from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .dashboard_ui import render_dashboard_html
from .projects_service import get_project, list_projects
from .search_service import search_index
from .signals_api import get_signal, list_signals


@dataclass(frozen=True)
class SignalsApiServerConfig:
    start_date: str
    end_date: str
    city: str | None = None
    live_fetch: bool = False
    timeout_seconds: int = 20
    max_retries: int = 2
    verify_ssl: bool = True


def _first(query: dict[str, list[str]], key: str) -> str | None:
    value = query.get(key)
    if not value:
        return None
    return value[0]


def _respond_json(handler: BaseHTTPRequestHandler, status_code: int, payload: dict) -> None:
    body = json.dumps(payload, indent=2).encode("utf-8")
    handler.send_response(status_code)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _respond_html(handler: BaseHTTPRequestHandler, status_code: int, html: str) -> None:
    body = html.encode("utf-8")
    handler.send_response(status_code)
    handler.send_header("Content-Type", "text/html; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def create_signals_api_handler(config: SignalsApiServerConfig) -> type[BaseHTTPRequestHandler]:
    class SignalsApiHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)

            if parsed.path == "/signals":
                try:
                    response = list_signals(
                        start_date=_first(query, "start_date") or config.start_date,
                        end_date=_first(query, "end_date") or config.end_date,
                        city=_first(query, "city") or config.city,
                        category=_first(query, "category"),
                        confidence=_first(query, "confidence"),
                        keyword=_first(query, "keyword"),
                        content_available=_first(query, "content_available"),
                        sort_by=_first(query, "sort_by") or "date",
                        sort_order=_first(query, "sort_order") or "desc",
                        limit=int(_first(query, "limit") or "100"),
                        offset=int(_first(query, "offset") or "0"),
                        live_fetch=config.live_fetch,
                        timeout_seconds=config.timeout_seconds,
                        max_retries=config.max_retries,
                        verify_ssl=config.verify_ssl,
                    )
                except ValueError as error:
                    _respond_json(self, 400, {"error": str(error)})
                    return

                _respond_json(
                    self,
                    200,
                    {
                        "items": [asdict(signal) for signal in response.items],
                        "total": response.total,
                        "limit": response.limit,
                        "offset": response.offset,
                    },
                )
                return

            if parsed.path.startswith("/signals/"):
                signal_id = parsed.path.split("/signals/", 1)[1]
                if not signal_id:
                    _respond_json(self, 400, {"error": "signal id is required"})
                    return

                try:
                    signal = get_signal(
                        signal_id=signal_id,
                        start_date=_first(query, "start_date") or config.start_date,
                        end_date=_first(query, "end_date") or config.end_date,
                        live_fetch=config.live_fetch,
                        timeout_seconds=config.timeout_seconds,
                        max_retries=config.max_retries,
                        verify_ssl=config.verify_ssl,
                    )
                except KeyError as error:
                    _respond_json(self, 404, {"error": str(error)})
                    return

                _respond_json(self, 200, asdict(signal))
                return

            if parsed.path == "/projects":
                try:
                    response = list_projects(
                        start_date=_first(query, "start_date") or config.start_date,
                        end_date=_first(query, "end_date") or config.end_date,
                        city=_first(query, "city") or config.city,
                        keyword=_first(query, "keyword"),
                        limit=int(_first(query, "limit") or "100"),
                        offset=int(_first(query, "offset") or "0"),
                        live_fetch=config.live_fetch,
                        timeout_seconds=config.timeout_seconds,
                        max_retries=config.max_retries,
                        verify_ssl=config.verify_ssl,
                    )
                except ValueError as error:
                    _respond_json(self, 400, {"error": str(error)})
                    return

                _respond_json(
                    self,
                    200,
                    {
                        "items": [asdict(project) for project in response.items],
                        "total": response.total,
                        "limit": response.limit,
                        "offset": response.offset,
                    },
                )
                return

            if parsed.path.startswith("/projects/"):
                project_id = parsed.path.split("/projects/", 1)[1]
                if not project_id:
                    _respond_json(self, 400, {"error": "project id is required"})
                    return

                try:
                    project = get_project(
                        project_id=project_id,
                        start_date=_first(query, "start_date") or config.start_date,
                        end_date=_first(query, "end_date") or config.end_date,
                        city=_first(query, "city") or config.city,
                        live_fetch=config.live_fetch,
                        timeout_seconds=config.timeout_seconds,
                        max_retries=config.max_retries,
                        verify_ssl=config.verify_ssl,
                    )
                except KeyError as error:
                    _respond_json(self, 404, {"error": str(error)})
                    return

                _respond_json(self, 200, asdict(project))
                return

            if parsed.path == "/dashboard":
                _respond_html(self, 200, render_dashboard_html())
                return

            if parsed.path == "/search":
                try:
                    query_text = _first(query, "q") or ""
                    response = search_index(
                        start_date=_first(query, "start_date") or config.start_date,
                        end_date=_first(query, "end_date") or config.end_date,
                        query=query_text,
                        city=_first(query, "city") or config.city,
                        meeting_body=_first(query, "body"),
                        category=_first(query, "category"),
                        confidence=_first(query, "confidence"),
                        live_fetch=config.live_fetch,
                        timeout_seconds=config.timeout_seconds,
                        max_retries=config.max_retries,
                        verify_ssl=config.verify_ssl,
                    )
                except ValueError as error:
                    _respond_json(self, 400, {"error": str(error)})
                    return

                _respond_json(self, 200, asdict(response))
                return

            if parsed.path == "/health":
                _respond_json(self, 200, {"status": "ok"})
                return

            _respond_json(self, 404, {"error": "not found"})

        def log_message(self, format: str, *args) -> None:
            return

    return SignalsApiHandler


def create_signals_api_server(
    host: str,
    port: int,
    config: SignalsApiServerConfig,
) -> ThreadingHTTPServer:
    handler = create_signals_api_handler(config)
    return ThreadingHTTPServer((host, port), handler)


def run_signals_api_server(host: str, port: int, config: SignalsApiServerConfig) -> None:
    server = create_signals_api_server(host=host, port=port, config=config)
    print(f"Signals API server listening on http://{host}:{port}")
    server.serve_forever()
