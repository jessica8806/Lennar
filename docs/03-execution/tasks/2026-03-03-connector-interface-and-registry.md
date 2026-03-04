# Task: Implement connector interface and adapter registry

## Linked docs
- PRD section(s): Core User Capabilities (Monitor government signals, Access meeting records), Data Freshness and Scope
- Architecture section(s): Functional Spec -> Platform Connectors, City Connector Map (Phase 1), Scheduler Behavior
- ADR(s): docs/02-architecture/adr/0001-template.md
- Roadmap milestone: Phase A — Platform Foundations

## Scope
- Define a platform connector interface contract used by all connector types.
- Implement adapter registry and router by platform type.
- Add city registry seed configuration for Phase 1 cities (city, platform, discovery URL, bodies).
- Ensure scheduler can iterate city registry and invoke router with dry-run support.

## Acceptance Criteria
- [ ] A single connector interface is documented and implemented for meeting discovery, agenda parsing, and document extraction.
- [ ] Router resolves connector implementation from platform type for all 6 required platforms.
- [ ] Phase 1 city registry includes all 10 cities and both tracked bodies.
- [ ] Dry-run execution logs intended connector invocation per city/body without downloading documents.
- [ ] Unit tests validate registry lookup and unsupported platform behavior.

## Implementation Notes
- Keep platform-specific logic out of city configs.
- Add an explicit unsupported-platform error path with actionable diagnostics.
- Keep interfaces stable for upcoming connector test harness work.

## Validation
- command: run unit tests for connector registry and router modules
- expected output: all connector routing tests pass; unsupported platform path returns deterministic error

## Rollout
- Land interface + registry first behind dry-run execution mode.
- Enable as default scheduler routing path after tests pass.

## Risks
- Prematurely narrow interface may block edge-case connectors.
- Registry/config drift if city map is duplicated in multiple files.