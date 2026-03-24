# Task: Build Granicus and Legistar connectors first

## Linked docs
- PRD section(s): Monitor government signals, Access meeting records, Monitor changes
- Architecture section(s): Functional Spec -> Platform Connectors, Meeting Discovery Requirements, Document Ingestion Requirements
- ADR(s): docs/02-architecture/adr/0001-template.md
- Roadmap milestone: Phase A — Platform Foundations

## Scope
- Implement production-grade Granicus and Legistar connector adapters.
- Support meeting discovery fields: meeting_date, meeting_title, meeting_body, agenda_url, minutes_url, video_url.
- Parse agenda items and attachment metadata required for downstream ingestion.
- Add fixture-based parser tests for representative HTML/pages per platform.

## Acceptance Criteria
- [x] Granicus connector discovers meetings and emits required fields for City Council and Planning Commission.
- [x] Legistar connector discovers meetings and emits required fields for City Council and Planning Commission.
- [x] Both connectors return stable IDs needed for change detection and dedupe.
- [x] Parser tests cover at least one normal case and one markup-variation case per platform.
- [x] Connector output conforms to shared interface contract.
- [x] Legistar document extraction emits valid `View.ashx` links for supporting documents.
- [x] Malformed synthetic document paths (e.g., `MeetingDetail.aspx?.../agenda.pdf`) are not emitted.

## Implementation Notes
- Normalize body names to configured canonical values.
- Preserve source URLs for traceability and debugging.
- Keep parsing tolerant to minor DOM/order changes.

## Validation
- command: run connector fixture tests and dry-run scheduler for Irvine, Anaheim, Huntington Beach, Newport Beach, Costa Mesa, Fullerton
- expected output: discovered meetings contain required fields; no schema validation errors

Implemented validation commands:
- `PYTHONPATH=src python3 -m unittest discover -s tests -v`
- `PYTHONPATH=src python3 -m civicsignal dry-harness --start-date 2026-03-01 --end-date 2026-03-31 --city-id fullerton --live --insecure`

## Rollout
- Enable for the six cities on these two platforms first.
- Track connector success rate in system health once available.

## Risks
- Platform markup drift can break brittle selectors.
- Meeting IDs may vary by page/context and require normalization.