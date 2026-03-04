from __future__ import annotations

import sys
from dataclasses import asdict
from pathlib import Path

from flask import Flask, Response, jsonify, request

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from civicsignal.dashboard_ui import render_dashboard_html
from civicsignal.projects_service import get_project, list_projects
from civicsignal.search_service import search_index
from civicsignal.signals_api import get_signal, list_signals

app = Flask(__name__)


def _cfg(key: str, default: str) -> str:
    value = request.args.get(key)
    if value:
        return value
    return default


def _bool_arg(key: str, default: bool = False) -> bool:
    value = request.args.get(key)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def _int_arg(key: str, default: int) -> int:
    value = request.args.get(key)
    if value is None:
        return default
    return int(value)


@app.get("/")
def root() -> Response:
    return Response(render_dashboard_html(), mimetype="text/html")


@app.get("/dashboard")
def dashboard() -> Response:
    return Response(render_dashboard_html(), mimetype="text/html")


@app.get("/health")
def health() -> Response:
    return jsonify({"status": "ok"})


@app.get("/signals")
def signals() -> Response:
    try:
        response = list_signals(
            start_date=_cfg("start_date", "2026-03-01"),
            end_date=_cfg("end_date", "2026-03-31"),
            city=request.args.get("city"),
            category=request.args.get("category"),
            confidence=request.args.get("confidence"),
            keyword=request.args.get("keyword"),
            content_available=request.args.get("content_available"),
            sort_by=request.args.get("sort_by", "date"),
            sort_order=request.args.get("sort_order", "desc"),
            limit=_int_arg("limit", 100),
            offset=_int_arg("offset", 0),
            live_fetch=_bool_arg("live", False),
            timeout_seconds=_int_arg("timeout", 20),
            max_retries=_int_arg("retries", 2),
            verify_ssl=not _bool_arg("insecure", False),
        )
        return jsonify(
            {
                "items": [asdict(item) for item in response.items],
                "total": response.total,
                "limit": response.limit,
                "offset": response.offset,
            }
        )
    except ValueError as error:
        return jsonify({"error": str(error)}), 400


@app.get("/signals/<signal_id>")
def signal_detail(signal_id: str) -> Response:
    try:
        signal = get_signal(
            signal_id=signal_id,
            start_date=_cfg("start_date", "2026-03-01"),
            end_date=_cfg("end_date", "2026-03-31"),
            live_fetch=_bool_arg("live", False),
            timeout_seconds=_int_arg("timeout", 20),
            max_retries=_int_arg("retries", 2),
            verify_ssl=not _bool_arg("insecure", False),
        )
        return jsonify(asdict(signal))
    except KeyError as error:
        return jsonify({"error": str(error)}), 404


@app.get("/projects")
def projects() -> Response:
    try:
        response = list_projects(
            start_date=_cfg("start_date", "2026-03-01"),
            end_date=_cfg("end_date", "2026-03-31"),
            city=request.args.get("city"),
            keyword=request.args.get("keyword"),
            limit=_int_arg("limit", 100),
            offset=_int_arg("offset", 0),
            live_fetch=_bool_arg("live", False),
            timeout_seconds=_int_arg("timeout", 20),
            max_retries=_int_arg("retries", 2),
            verify_ssl=not _bool_arg("insecure", False),
        )
        return jsonify(
            {
                "items": [asdict(item) for item in response.items],
                "total": response.total,
                "limit": response.limit,
                "offset": response.offset,
            }
        )
    except ValueError as error:
        return jsonify({"error": str(error)}), 400


@app.get("/projects/<project_id>")
def project_detail(project_id: str) -> Response:
    try:
        project = get_project(
            project_id=project_id,
            start_date=_cfg("start_date", "2026-03-01"),
            end_date=_cfg("end_date", "2026-03-31"),
            city=request.args.get("city"),
            live_fetch=_bool_arg("live", False),
            timeout_seconds=_int_arg("timeout", 20),
            max_retries=_int_arg("retries", 2),
            verify_ssl=not _bool_arg("insecure", False),
        )
        return jsonify(asdict(project))
    except KeyError as error:
        return jsonify({"error": str(error)}), 404


@app.get("/search")
def search() -> Response:
    try:
        response = search_index(
            start_date=_cfg("start_date", "2026-03-01"),
            end_date=_cfg("end_date", "2026-03-31"),
            query=request.args.get("q", ""),
            city=request.args.get("city"),
            meeting_body=request.args.get("body"),
            category=request.args.get("category"),
            confidence=request.args.get("confidence"),
            live_fetch=_bool_arg("live", False),
            timeout_seconds=_int_arg("timeout", 20),
            max_retries=_int_arg("retries", 2),
            verify_ssl=not _bool_arg("insecure", False),
        )
        return jsonify(asdict(response))
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
