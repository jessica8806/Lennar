# CivicSignal

Municipal meeting intelligence platform for discovering, parsing, and classifying actionable government signals from Orange County city meetings.

## What this repo contains

This repository is organized in a documentation-first structure to support product clarity, architecture decisions, and execution discipline:

- `docs/00-context` — vision and constraints
- `docs/01-product` — user requirements (PRD)
- `docs/02-architecture` — system architecture, functional spec, connector registry, and ADRs
- `docs/03-execution` — roadmap and task planning
- `docs/04-operations` — runbooks and operational procedures
- `docs/05-metrics` — KPI definitions and targets

## Phase 1 scope

- Geography: 10 Orange County cities
- Bodies: City Council + Planning Commission
- Cadence: daily refresh
- Backfill: 12 months
- Document scope: agenda, agenda packets, staff reports (<= 25 MB)

## Build principles

- Use connector templates (platform-driven), not city-specific scrapers
- Keep ingestion idempotent via hashing + change detection
- Extract multiple signals per agenda item when needed
- Group signal history into project entities over time
- Make system health and connector quality visible by default

## Implementation quickstart

Core Python implementation now exists under `src/civicsignal` with:
- connector interface, registry, and platform adapters
- phase-1 city registry for all 10 configured cities
- dry-run scheduler and connector harness
- contract validation and unit tests

Run tests:
- `PYTHONPATH=src python3 -m unittest discover -s tests -v`

Run dry scheduler:
- `PYTHONPATH=src python3 -m civicsignal dry-scheduler --start-date 2026-03-01 --end-date 2026-03-03`
- `PYTHONPATH=src python3 -m civicsignal dry-scheduler --start-date 2026-03-01 --end-date 2026-03-03 --live`

Run dry harness (all cities):
- `PYTHONPATH=src python3 -m civicsignal dry-harness --start-date 2026-03-01 --end-date 2026-03-03`
- `PYTHONPATH=src python3 -m civicsignal dry-harness --start-date 2026-03-01 --end-date 2026-03-03 --live`
- `PYTHONPATH=src python3 -m civicsignal dry-harness --start-date 2026-03-01 --end-date 2026-03-03 --live --insecure` (diagnostics only)

Live mode interpretation:
- `live_fetch_requested=true` confirms live fetching was attempted.
- `fallback_count=0` means the connector parsed fetched HTML without fallback.
- `fallback_count>0` means it fell back to sample parsing (fetch failed or live parse returned no meetings).
- harness `status` is `degraded` when fallback occurs.
- `--insecure` disables SSL verification for troubleshooting environment certificate issues.

Run dry harness (single city):
- `PYTHONPATH=src python3 -m civicsignal dry-harness --start-date 2026-03-01 --end-date 2026-03-03 --city-id irvine`

Run change detection (first pass builds baseline):
- `PYTHONPATH=src python3 -m civicsignal dry-change-detect --start-date 2026-03-01 --end-date 2026-03-31 --city-id fullerton --state-path .civicsignal/change-state.json`

Run change detection (second pass should move to unchanged when source is stable):
- `PYTHONPATH=src python3 -m civicsignal dry-change-detect --start-date 2026-03-01 --end-date 2026-03-31 --city-id fullerton --state-path .civicsignal/change-state.json`

Run signal generation summary:
- `PYTHONPATH=src python3 -m civicsignal dry-signals --start-date 2026-03-01 --end-date 2026-03-31 --city-id fullerton`

Run signal generation with full payloads:
- `PYTHONPATH=src python3 -m civicsignal dry-signals --start-date 2026-03-01 --end-date 2026-03-31 --city-id fullerton --include-signals`

Run system health diagnostics:
- `PYTHONPATH=src python3 -m civicsignal dry-system-health --start-date 2026-03-01 --end-date 2026-03-31 --city-id fullerton`

System health metrics include:
- city run counters (meetings/documents/signals)
- content availability and title-only rates
- document parse success rate
- status thresholds: healthy / warning / failed
- admin action prompts when title-only rates are high

Signal output quality semantics:
- `summary_source` values: `staff_report`, `agenda_packet`, `item_description`, `title_only`.
- `content_available=false` indicates summary fallback due to missing or low-quality text.
- `summary` is explicitly prefixed with `Title-only:` when fallback is used.
- Legistar `supporting_documents` should use `View.ashx` endpoints when available.
