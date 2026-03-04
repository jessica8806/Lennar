from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from .change_runner import run_change_detection
from .harness import run_connector_dry_harness
from .api_server import SignalsApiServerConfig, run_signals_api_server
from .scheduler import run_dry_scheduler
from .signals_api import get_signal, list_signals
from .signal_runner import run_signal_generation
from .system_health import run_system_health


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CivicSignal tooling")
    subparsers = parser.add_subparsers(dest="command", required=True)

    dry_scheduler = subparsers.add_parser("dry-scheduler", help="Run dry scheduler across configured cities")
    dry_scheduler.add_argument("--start-date", required=True)
    dry_scheduler.add_argument("--end-date", required=True)
    dry_scheduler.add_argument("--live", action="store_true", help="Fetch live HTML from city discovery URLs")
    dry_scheduler.add_argument("--timeout-seconds", type=int, default=20)
    dry_scheduler.add_argument("--max-retries", type=int, default=2)
    dry_scheduler.add_argument("--insecure", action="store_true", help="Disable SSL certificate verification (diagnostics only)")

    dry_harness = subparsers.add_parser("dry-harness", help="Run connector dry harness")
    dry_harness.add_argument("--start-date", required=True)
    dry_harness.add_argument("--end-date", required=True)
    dry_harness.add_argument("--city-id", required=False)
    dry_harness.add_argument("--live", action="store_true", help="Fetch live HTML from city discovery URLs")
    dry_harness.add_argument("--timeout-seconds", type=int, default=20)
    dry_harness.add_argument("--max-retries", type=int, default=2)
    dry_harness.add_argument("--insecure", action="store_true", help="Disable SSL certificate verification (diagnostics only)")
    dry_harness.add_argument("--debug-meetings", action="store_true", help="Include per-meeting agenda extraction diagnostics")

    change_detect = subparsers.add_parser("dry-change-detect", help="Run change detection based on meeting/document hashes")
    change_detect.add_argument("--start-date", required=True)
    change_detect.add_argument("--end-date", required=True)
    change_detect.add_argument("--city-id", required=False)
    change_detect.add_argument("--live", action="store_true", help="Fetch live HTML from city discovery URLs")
    change_detect.add_argument("--timeout-seconds", type=int, default=20)
    change_detect.add_argument("--max-retries", type=int, default=2)
    change_detect.add_argument("--insecure", action="store_true", help="Disable SSL certificate verification (diagnostics only)")
    change_detect.add_argument("--state-path", default=".civicsignal/change-state.json")
    change_detect.add_argument("--no-persist", action="store_true", help="Compute deltas without updating state")

    signal_generate = subparsers.add_parser("dry-signals", help="Run rule-based signal generation")
    signal_generate.add_argument("--start-date", required=True)
    signal_generate.add_argument("--end-date", required=True)
    signal_generate.add_argument("--city-id", required=False)
    signal_generate.add_argument("--live", action="store_true", help="Fetch live HTML from city discovery URLs")
    signal_generate.add_argument("--timeout-seconds", type=int, default=20)
    signal_generate.add_argument("--max-retries", type=int, default=2)
    signal_generate.add_argument("--insecure", action="store_true", help="Disable SSL certificate verification (diagnostics only)")
    signal_generate.add_argument("--include-signals", action="store_true", help="Include full signal payloads in output")

    api_signals = subparsers.add_parser("api-signals", help="Signals API surface (list/detail)")
    api_signals.add_argument("--start-date", required=True)
    api_signals.add_argument("--end-date", required=True)
    api_signals.add_argument("--signal-id", required=False, help="If provided, returns one signal detail")
    api_signals.add_argument("--city", required=False)
    api_signals.add_argument("--category", required=False)
    api_signals.add_argument("--confidence", required=False)
    api_signals.add_argument("--keyword", required=False)
    api_signals.add_argument("--content-available", required=False, choices=["true", "false"])
    api_signals.add_argument("--sort-by", default="date", choices=["date", "confidence"])
    api_signals.add_argument("--sort-order", default="desc", choices=["asc", "desc"])
    api_signals.add_argument("--limit", type=int, default=100)
    api_signals.add_argument("--offset", type=int, default=0)
    api_signals.add_argument("--live", action="store_true", help="Fetch live HTML from city discovery URLs")
    api_signals.add_argument("--timeout-seconds", type=int, default=20)
    api_signals.add_argument("--max-retries", type=int, default=2)
    api_signals.add_argument("--insecure", action="store_true", help="Disable SSL certificate verification (diagnostics only)")

    serve_api = subparsers.add_parser("serve-signals-api", help="Run HTTP server for GET /signals and GET /signals/{id}")
    serve_api.add_argument("--start-date", required=True)
    serve_api.add_argument("--end-date", required=True)
    serve_api.add_argument("--city", required=False)
    serve_api.add_argument("--host", default="127.0.0.1")
    serve_api.add_argument("--port", type=int, default=8080)
    serve_api.add_argument("--live", action="store_true", help="Fetch live HTML from city discovery URLs")
    serve_api.add_argument("--timeout-seconds", type=int, default=20)
    serve_api.add_argument("--max-retries", type=int, default=2)
    serve_api.add_argument("--insecure", action="store_true", help="Disable SSL certificate verification (diagnostics only)")

    system_health = subparsers.add_parser("dry-system-health", help="Run system health diagnostics and KPI rollups")
    system_health.add_argument("--start-date", required=True)
    system_health.add_argument("--end-date", required=True)
    system_health.add_argument("--city-id", required=False)
    system_health.add_argument("--live", action="store_true", help="Fetch live HTML from city discovery URLs")
    system_health.add_argument("--timeout-seconds", type=int, default=20)
    system_health.add_argument("--max-retries", type=int, default=2)
    system_health.add_argument("--insecure", action="store_true", help="Disable SSL certificate verification (diagnostics only)")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "dry-scheduler":
        logs = run_dry_scheduler(
            start_date=args.start_date,
            end_date=args.end_date,
            live_fetch=args.live,
            timeout_seconds=args.timeout_seconds,
            max_retries=args.max_retries,
            verify_ssl=not args.insecure,
        )
        print(json.dumps([asdict(log) for log in logs], indent=2))
        return 0

    if args.command == "dry-harness":
        results = run_connector_dry_harness(
            start_date=args.start_date,
            end_date=args.end_date,
            city_id=args.city_id,
            live_fetch=args.live,
            timeout_seconds=args.timeout_seconds,
            max_retries=args.max_retries,
            verify_ssl=not args.insecure,
            debug_meetings=args.debug_meetings,
        )
        output = []
        for result in results:
            payload = asdict(result)
            payload["errors"] = [asdict(error) for error in result.errors]
            output.append(payload)
        print(json.dumps(output, indent=2))
        return 0

    if args.command == "dry-change-detect":
        summaries = run_change_detection(
            start_date=args.start_date,
            end_date=args.end_date,
            city_id=args.city_id,
            live_fetch=args.live,
            timeout_seconds=args.timeout_seconds,
            max_retries=args.max_retries,
            verify_ssl=not args.insecure,
            state_path=args.state_path,
            persist=not args.no_persist,
        )
        print(json.dumps([asdict(summary) for summary in summaries], indent=2))
        return 0

    if args.command == "dry-signals":
        summaries, signals = run_signal_generation(
            start_date=args.start_date,
            end_date=args.end_date,
            city_id=args.city_id,
            live_fetch=args.live,
            timeout_seconds=args.timeout_seconds,
            max_retries=args.max_retries,
            verify_ssl=not args.insecure,
        )
        payload = {
            "summary": [asdict(summary) for summary in summaries],
            "signals_count": len(signals),
        }
        if args.include_signals:
            payload["signals"] = [asdict(signal) for signal in signals]
        print(json.dumps(payload, indent=2))
        return 0

    if args.command == "dry-system-health":
        summary = run_system_health(
            start_date=args.start_date,
            end_date=args.end_date,
            city_id=args.city_id,
            live_fetch=args.live,
            timeout_seconds=args.timeout_seconds,
            max_retries=args.max_retries,
            verify_ssl=not args.insecure,
        )
        payload = {
            "cities": [asdict(city_summary) for city_summary in summary.cities],
            "totals": asdict(summary.totals),
        }
        print(json.dumps(payload, indent=2))
        return 0

    if args.command == "api-signals":
        if args.signal_id:
            signal = get_signal(
                signal_id=args.signal_id,
                start_date=args.start_date,
                end_date=args.end_date,
                live_fetch=args.live,
                timeout_seconds=args.timeout_seconds,
                max_retries=args.max_retries,
                verify_ssl=not args.insecure,
            )
            print(json.dumps(asdict(signal), indent=2))
            return 0

        response = list_signals(
            start_date=args.start_date,
            end_date=args.end_date,
            city=args.city,
            category=args.category,
            confidence=args.confidence,
            keyword=args.keyword,
            content_available=args.content_available,
            sort_by=args.sort_by,
            sort_order=args.sort_order,
            limit=args.limit,
            offset=args.offset,
            live_fetch=args.live,
            timeout_seconds=args.timeout_seconds,
            max_retries=args.max_retries,
            verify_ssl=not args.insecure,
        )
        payload = {
            "items": [asdict(signal) for signal in response.items],
            "total": response.total,
            "limit": response.limit,
            "offset": response.offset,
        }
        print(json.dumps(payload, indent=2))
        return 0

    if args.command == "serve-signals-api":
        run_signals_api_server(
            host=args.host,
            port=args.port,
            config=SignalsApiServerConfig(
                start_date=args.start_date,
                end_date=args.end_date,
                city=args.city,
                live_fetch=args.live,
                timeout_seconds=args.timeout_seconds,
                max_retries=args.max_retries,
                verify_ssl=not args.insecure,
            ),
        )
        return 0

    parser.print_help()
    return 1
