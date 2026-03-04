# Task: Projects Grouping Service

## Linked docs
- PRD section(s): docs/01-product/phase2-definition.md (Project View)
- Architecture section(s): docs/02-architecture/phase2-functional-spec.md (Projects UI)
- ADR(s): docs/02-architecture/adr/0001-template.md
- Roadmap milestone: Phase G — Product Surface (Phase 2)

## Scope
- Implement grouping service and read models for project timelines.
- Expose grouped signals with project metadata.
- Support timeline ordering by detected date.

## Acceptance Criteria
- [x] Related signals can be grouped under a project entity.
- [x] Project timeline returns first detected and latest activity dates.
- [x] Project timeline entries are clickable signal references.
- [x] Grouping quality is testable with fixture datasets.

## Implementation Notes
- Reuse existing project entity heuristics from architecture docs.
- Keep grouping deterministic for repeatability.

## Validation
- command: `PYTHONPATH=src python3 -m unittest tests/test_projects_service.py tests/test_signals_http_api.py`
- expected output: grouping service and `/projects` endpoint tests pass with deterministic project/timeline payloads

## Rollout
- Integrated with `GET /projects` and `GET /projects/{id}` on shared HTTP transport layer.

## Risks
- Over-grouping may combine unrelated municipal actions.
