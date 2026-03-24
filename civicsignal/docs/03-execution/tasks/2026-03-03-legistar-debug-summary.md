# Task: Legistar Debug Summary (Root Cause + Fix Plan)

## Linked docs
- PRD section(s): docs/01-product/phase2-definition.md (Signals Dashboard, Signal Detail, Signal Search)
- Architecture section(s): docs/02-architecture/phase2-functional-spec.md (Signals UI, Admin UX, API Surfaces)
- ADR(s): docs/02-architecture/adr/0001-template.md
- Roadmap milestone: Phase G — Product Surface (Phase 2)

## Current state (confirmed)
- Connectors + harness + change-detect execute end-to-end.
- Honest summary gating works (`summary_source=title_only`, low confidence fallback behavior).
- Dry-signals previously generated synthetic one-item-per-meeting outputs for Legistar paths.

## Root cause
- Stub/test meeting IDs leaked into execution paths (`MeetingDetail.aspx?ID=100/101`), creating invalid detail pages.
- Agenda parsing path was using stub `parse_agenda` behavior for Legistar, producing one synthetic item per meeting.

## Scope
- Add diagnostics to isolate connector → meeting parser → agenda extractor → signal input.
- Block fallback-derived/stub-like IDs in live mode.
- Parse agenda rows from Legistar MeetingDetail pages.
- Expand harness/system diagnostics to reflect extraction depth.

## Acceptance Criteria
- [x] `dry-harness --debug-meetings` returns per-meeting extraction diagnostics.
- [x] Live-mode Legistar discovery does not emit meetings when live fetch fails.
- [x] Stub-like meeting IDs are rejected in live-mode discovery.
- [x] `dry-signals` no longer reports fixed 2 agenda items for Legistar dry runs.
- [x] Add document text extraction counters (`documents_downloaded`, `documents_text_extracted_ok`) into signal run path.
- [x] Raise `content_available` above title-only baseline via packet/staff report text extraction.

## Implementation Notes
- Added `parse_legistar_agenda_items(...)` and wired `LegistarConnector.parse_agenda(...)` to MeetingDetail fetch/parse flow.
- Added richer harness diagnostics and `--debug-meetings` CLI option.
- Replaced fallback sample IDs with realistic-range IDs and preserved GUID in `View.ashx` derivation.

## Validation
- command: `PYTHONPATH=src python3 -m unittest`
- expected output: all tests pass including Legistar parser/harness/live-fetch guard regressions

- command: `PYTHONPATH=src python3 -m civicsignal dry-harness --start-date 2026-03-01 --end-date 2026-03-31 --city-id costa-mesa --debug-meetings`
- expected output: agenda extraction diagnostics show per-meeting agenda item counts > 10

- command: `PYTHONPATH=src python3 -m civicsignal dry-signals --start-date 2026-03-01 --end-date 2026-03-31 --city-id costa-mesa --include-signals`
- expected output: `agenda_items_processed` and `signals_generated` reflect multi-item meetings (not fixed at 2)

## Rollout
- Keep this hardening active while Priority 6 API continues, then proceed to content extraction milestone.

## Risks
- Live sources with dynamic agenda rendering may still need source-specific selectors.
- Packet-level text can over-broaden classification unless item-level context windows and taxonomy tuning are applied.
