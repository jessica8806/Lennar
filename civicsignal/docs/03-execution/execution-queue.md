# Execution Queue (No-Week Planning)

This queue defines implementation order by dependency and impact, independent of calendar weeks.

## Queue Rules
- Pull the highest-priority unblocked item first.
- Do not start a lower-priority item if a prerequisite item is still open.
- Close each item only when validation criteria in its task doc are met.

## Priority Order
1. Connector interface and adapter registry  
   - Task: `docs/03-execution/tasks/2026-03-03-connector-interface-and-registry.md`  
   - Depends on: none
2. Granicus and Legistar connectors  
   - Task: `docs/03-execution/tasks/2026-03-03-granicus-and-legistar-connectors.md`  
   - Depends on: connector interface and registry
3. Change detection hashing  
   - Task: `docs/03-execution/tasks/2026-03-03-change-detection-hashing.md`  
   - Depends on: connector outputs and ingestion baseline
4. Signal schema and confidence scoring  
   - Task: `docs/03-execution/tasks/2026-03-03-signal-schema-and-confidence.md`  
   - Depends on: agenda item and document ingestion shape stabilized
5. System health and dry-run harness  
   - Task: `docs/03-execution/tasks/2026-03-03-system-health-and-dry-run-harness.md`  
   - Depends on: connector execution path and error taxonomy available
6. Signals API  
   - Task: `docs/03-execution/tasks/2026-03-03-signals-api.md`  
   - Depends on: signal schema and confidence scoring complete
7. Projects grouping service  
   - Task: `docs/03-execution/tasks/2026-03-03-projects-grouping-service.md`  
   - Depends on: signals API and project entity grouping heuristics
8. Search index  
   - Task: `docs/03-execution/tasks/2026-03-03-search-index.md`  
   - Depends on: documents + signals data contracts stabilized
9. Dashboard UI  
   - Task: `docs/03-execution/tasks/2026-03-03-dashboard-ui.md`  
   - Depends on: signals API and search index baseline
10. Admin tools  
   - Task: `docs/03-execution/tasks/2026-03-03-admin-tools.md`  
   - Depends on: system health and connector diagnostics outputs
11. System health UI  
   - Task: `docs/03-execution/tasks/2026-03-03-system-health-ui.md`  
   - Depends on: system health metrics and status thresholds complete

## Parallelization Guidance
- Connector parser fixture authoring can run in parallel with registry tests once interface contract is frozen.
- Signal schema validation can begin before full model-assisted extraction if taxonomy enums are finalized.

## Definition of Ready (per item)
- Linked docs complete
- Acceptance criteria testable
- Validation command defined
- Owner identified

## Definition of Done (per item)
- Acceptance criteria checked
- Validation command run with expected output
- Risks reviewed and any follow-up tasks logged
