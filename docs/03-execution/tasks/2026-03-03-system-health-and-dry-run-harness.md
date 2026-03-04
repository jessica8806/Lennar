# Task: Build system health and connector dry-run harness

## Linked docs
- PRD section(s): Default User Experience, Monitor government signals
- Architecture section(s): Functional Spec -> System Health, Scheduler Behavior
- ADR(s): docs/02-architecture/adr/0001-template.md
- Roadmap milestone: Phase F — Backfill + Hardening

## Scope
- Implement connector dry-run harness for targeted city/body/date-range execution.
- Capture structured results: discovered meetings, parse errors, download attempts, timings.
- Define system health outputs for last scrape, connector status, errors, and throughput counters.
- Provide operator-facing report format for runbook triage workflows.

## Acceptance Criteria
- [x] Dry-run can execute per city/body without writing production records.
- [x] Harness output includes connector status, error categories, and timing metrics.
- [x] Health summary includes city-level counters and run-level totals.
- [x] Failed connectors return actionable diagnostics tied to source URLs.
- [x] Output supports runbook incident diagnosis steps.
- [x] Derived KPI metrics are included: content availability rate, doc parse success rate, title-only rate.
- [x] Status thresholds classify `healthy`/`warning`/`failed` and avoid false-green title-only runs.
- [x] Admin action prompt is emitted when title-only rates are elevated.

## Implementation Notes
- Keep dry-run mode deterministic and safe for repeated execution.
- Add machine-readable output for future dashboard/API integration.
- Align metric names with KPI and alert definitions.

## Validation
- command: run dry-run harness over all 10 cities for last 30 days in non-persistent mode
- expected output: per-platform status summary, error breakdown, and city/body health report generated

Implemented validation command:
- `PYTHONPATH=src python3 -m civicsignal dry-system-health --start-date 2026-03-01 --end-date 2026-03-31 --city-id fullerton`

## Rollout
- Start as CLI/internal endpoint used by engineering and on-call.
- Integrate with System Health UI after schema stabilization.

## Risks
- High variance across source systems may require connector-specific diagnostics.
- Large dry-run windows can increase runtime without pagination controls.