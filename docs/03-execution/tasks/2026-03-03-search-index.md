# Task: Search Index

## Linked docs
- PRD section(s): docs/01-product/phase2-definition.md (Document Library, Signal Search)
- Architecture section(s): docs/02-architecture/phase2-functional-spec.md (Search UX)
- ADR(s): docs/02-architecture/adr/0001-template.md
- Roadmap milestone: Phase G — Product Surface (Phase 2)

## Scope
- Build unified search index across signals, meetings, documents, and projects.
- Support keyword search and entity-specific filters.
- Return grouped result sets for UI rendering.

## Acceptance Criteria
- [x] Search returns signals, meetings, documents, and projects.
- [x] Filters for city, body, category, confidence, date range are supported.
- [x] Document results include snippet previews and links.
- [x] Search responses are performant for Phase 2 dataset assumptions.

## Implementation Notes
- Use a normalized indexing schema compatible with future ranking.
- Track result source type for grouped UI display.

## Validation
- command: `PYTHONPATH=src python3 -m unittest tests/test_search_service.py tests/test_signals_http_api.py`
- expected output: search service and `/search` transport tests pass with grouped entities and filter coverage

## Rollout
- Launch as backend dependency for Dashboard, Signals, Documents, and Search pages.

## Risks
- Inconsistent tokenization can reduce recall/precision.
