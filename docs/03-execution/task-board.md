# Task Board

Source of truth for active execution status, using priority and dependency flow.

## Status Legend
- Todo: scoped and ready
- In Progress: currently being executed
- Blocked: waiting on dependency or decision
- Done: acceptance criteria validated

## Board
| Priority | Task | Status | Depends on | Owner |
|---:|---|---|---|---|
| 1 | Connector interface and adapter registry | Done | None | Engineering |
| 2 | Granicus and Legistar connectors | Done (live routing + agenda extraction hardening) | Connector interface and adapter registry | Engineering |
| 3 | Change detection hashing | Done (hash + snapshot + delta) | Connector outputs + ingestion baseline | Engineering |
| 4 | Signal schema and confidence scoring | Done (schema + validation + runner) | Ingestion shape stabilized | Engineering + Product |
| 5 | System health and dry-run harness | Done (deep diagnostics + extraction counters) | Connector execution path + error taxonomy | Engineering + SRE |
| 6 | Signals API | Done (service + HTTP transport + tests) | Signal schema and confidence scoring | Engineering |
| 7 | Projects grouping service | Done (service + /projects API + tests) | Signals API + grouping heuristics | Engineering |
| 8 | Search index | Done (service + /search API + tests) | Documents/signals contracts stabilized | Engineering |
| 9 | Dashboard UI | Done (/dashboard UI route + tests) | Signals API + search index baseline | Engineering |
| 10 | Admin tools | Todo | Health diagnostics + connector dry-run outputs | Engineering |
| 11 | System health UI | Todo | System health metrics + thresholds | Engineering + SRE |

## Review checkpoint (current)
- Completed: Priority 6 HTTP transport for Signals API (`GET /signals`, `GET /signals/{id}`, `/health`) with `serve-signals-api` command.
- Completed: Priority 7 projects grouping service (`GET /projects`, `GET /projects/{id}`) with timeline payloads and deterministic grouping heuristics.
- Completed: Priority 8 search index service (`GET /search`) returning grouped signals/projects/meetings/documents with filters and snippets.
- Completed: Priority 9 dashboard UI route (`/dashboard`) with required sections, filters, sortable signals table, cards, and quality badge mapping.
- Completed: Step B content extraction wired for live runs (agenda packet PDF download + text extraction + per-item context).
- Completed: Step C taxonomy/trigger tuning to reduce over-classification noise.
- Completed: CLI compatibility hardening so `python3` runs without `pypdf` installed in non-venv environments.
- Validation command:
  - `PYTHONPATH=src python3 -m unittest`
  - `PYTHONPATH=src python3 -m civicsignal serve-signals-api --start-date 2026-03-01 --end-date 2026-03-03 --city fullerton --host 127.0.0.1 --port 8092`
  - `curl 'http://127.0.0.1:8092/signals?limit=2'`
  - `curl 'http://127.0.0.1:8092/projects?limit=2'`
  - `curl 'http://127.0.0.1:8092/search?q=planning'`
  - `curl 'http://127.0.0.1:8092/dashboard'`
  - `curl 'http://127.0.0.1:8092/health'`
- Expected check:
  - HTTP endpoints return schema-compliant JSON and handle invalid/unknown inputs with typed errors.
  - Signals API tests and transport tests pass in CI.
  - Projects API returns project metadata (`project_name`, `first_detected`, `latest_activity`) and timeline entries with `signal_id` references.
  - Search API returns grouped entities with city/body/category/confidence/date-compatible filtering semantics.
  - Dashboard route renders required sections and client controls for filters/sort plus summary-source quality badges.
  - Average signals per agenda item remains near 1-2 range after trigger tuning.
- Next review: start Priority 10 (Admin tools).

## Update Procedure
1. Pull next unblocked Todo item.
2. Move item to In Progress.
3. Run validation command from the linked task doc.
4. Mark Done only when acceptance criteria are checked.
