# Task: System Health UI

## Linked docs
- PRD section(s): docs/01-product/phase2-definition.md (System Health Dashboard)
- Architecture section(s): docs/02-architecture/phase2-functional-spec.md (System Health Admin UX)
- ADR(s): docs/02-architecture/adr/0001-template.md
- Roadmap milestone: Phase G — Product Surface (Phase 2)

## Scope
- Build UI for city-level and run-level health diagnostics.
- Display status and KPI metrics (content availability, parse success, title-only rate).
- Surface admin action prompts for extraction bottlenecks.

## Acceptance Criteria
- [ ] Health UI renders city and totals summaries from diagnostics endpoint.
- [ ] Status thresholds (healthy/warning/failed) are visually distinct.
- [ ] KPI rates are visible with clear definitions.
- [ ] Action prompts are visible when title-only rates are elevated.

## Implementation Notes
- Avoid false-green rendering when extraction coverage is low.
- Prioritize actionable troubleshooting context.

## Validation
- command: run system health UI tests against fixed diagnostics fixtures
- expected output: status, KPI, and action prompt rendering match backend payloads

## Rollout
- Release concurrently with admin tools and dashboard integration.

## Risks
- Misaligned thresholds between backend and UI can confuse operators.
