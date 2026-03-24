# Task: Dashboard UI

## Linked docs
- PRD section(s): docs/01-product/phase2-definition.md (Signals Dashboard)
- Architecture section(s): docs/02-architecture/phase2-functional-spec.md (Dashboard, Signals UI)
- ADR(s): docs/02-architecture/adr/0001-template.md
- Roadmap milestone: Phase G — Product Surface (Phase 2)

## Scope
- Implement dashboard sections: New Signals (24h), Signals by Category, Signals by City, Trending Projects.
- Implement Signals table columns/filters/sorting per spec.
- Render signal quality badges from `summary_source`.

## Acceptance Criteria
- [x] Dashboard renders required summary sections and charts.
- [x] Signals table supports required columns and filters.
- [x] Signal cards show city/body/date/type/confidence/summary/source link.
- [x] Quality badge is visible and correctly mapped to summary source.

## Implementation Notes
- Keep UI default clear about title-only content while extraction backlog remains open.
- Avoid hiding diagnostics signals from admin views.

## Validation
- command: `PYTHONPATH=src python3 -m unittest tests/test_signals_http_api.py`
- expected output: `/dashboard` route test confirms required sections, filters, table, and quality badge hooks are present

## Rollout
- Released on shared API server transport at `GET /dashboard` after Signals API and Search index baseline completion.

## Risks
- UI may appear noisy if ranking is not introduced early.
