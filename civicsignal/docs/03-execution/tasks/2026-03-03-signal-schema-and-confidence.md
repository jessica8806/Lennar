# Task: Implement signal schema and confidence scoring

## Linked docs
- PRD section(s): Signal Taxonomy, Signal Confidence, Core User Capabilities
- Architecture section(s): Functional Spec -> Signal Extraction, Signal Object Schema, Database Schema (Signals)
- ADR(s): docs/02-architecture/adr/0001-template.md
- Roadmap milestone: Phase D — Signal Engine + Grouping

## Scope
- Define canonical signal schema and storage contract.
- Implement category assignment constrained to the 12 PRD categories.
- Implement confidence scoring enum (High/Medium/Low) with deterministic policy.
- Support multiple signals per agenda item with one primary category per signal.

## Acceptance Criteria
- [x] Signal schema includes required fields from functional spec.
- [x] Category assignment rejects unknown/non-PRD categories.
- [x] Confidence value is always present and in allowed enum.
- [x] One agenda item can persist multiple independent signals.
- [x] Validation tests cover taxonomy and confidence constraints.
- [x] Summary quality gates enforce title-only labeling and low confidence when no meaningful content exists.
- [x] Summary provenance is captured via `summary_source` and `content_available`.

## Implementation Notes
- Keep schema versioned for future expansion.
- Separate extraction logic from final validation/enforcement.
- Preserve source references and supporting documents for auditability.

## Validation
- command: run schema validation tests with mixed valid/invalid signal payloads
- expected output: valid payloads pass; invalid category/confidence payloads fail with clear errors

Implemented validation commands:
- `PYTHONPATH=src python3 -m unittest discover -s tests -v`
- `PYTHONPATH=src python3 -m civicsignal dry-signals --start-date 2026-03-01 --end-date 2026-03-31 --city-id fullerton --include-signals`

## Rollout
- Start with rule-based baseline scoring and add model-assisted classification iteratively.

## Risks
- Taxonomy edge cases may reduce confidence consistency.
- Overly strict validation may block ingestion if upstream extraction quality is low.