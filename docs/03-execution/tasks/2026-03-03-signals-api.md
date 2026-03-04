# Task: Signals API

## Linked docs
- PRD section(s): docs/01-product/phase2-definition.md (Signals Dashboard, Signal Detail, Signal Search)
- Architecture section(s): docs/02-architecture/phase2-functional-spec.md (Signals UI, API Surfaces)
- ADR(s): docs/02-architecture/adr/0001-template.md
- Roadmap milestone: Phase G — Product Surface (Phase 2)

## Scope
- Implement `GET /signals` list behavior with filter/sort/pagination semantics.
- Implement `GET /signals/{id}` detail behavior for a single signal record.
- Return signal quality fields required by Phase 2 UI.

## Acceptance Criteria
- [ ] Implement list and detail API surfaces for signals.
- [ ] Support filters: city, category, confidence, date, keyword, content availability.
- [ ] Provide sort options for date and confidence.
- [ ] Return quality fields: `summary_source`, `content_available`, `extraction_notes`.
- [ ] Invalid query arguments return typed validation errors.

## Implementation Notes
- Keep response shape stable for dashboard and signal detail pages.
- Preserve source links and supporting document URLs in response payloads.
- Start with service + CLI contract, then expose over HTTP transport in follow-on step.

## Validation
- command: `PYTHONPATH=src python3 -m unittest tests/test_signals_api.py`
- expected output: list/detail/filter/sort/validation tests pass

## Rollout
- Ship behind Phase 2 feature gate and pair with dashboard integration task.

## Risks
- API shape churn can block UI implementation if response contracts are unstable.
