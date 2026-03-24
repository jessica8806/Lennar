# Task: Admin Tools

## Linked docs
- PRD section(s): docs/01-product/phase2-definition.md (Signal Discovery Mode, Connector Dry Run Tool)
- Architecture section(s): docs/02-architecture/phase2-functional-spec.md (Admin UX)
- ADR(s): docs/02-architecture/adr/0001-template.md
- Roadmap milestone: Phase G — Product Surface (Phase 2)

## Scope
- Implement admin pages for Connector Tests, Signal Discovery, and Taxonomy controls.
- Add dry-run execution controls for city/date selection.
- Add phrase and entity frequency views with export support.

## Acceptance Criteria
- [ ] Connector test UI runs dry-run and displays run outputs.
- [ ] Signal discovery UI shows top phrases, bigrams, trigrams, and entities.
- [ ] Phrase/frequency export is available.
- [ ] Taxonomy admin controls can support future rule tuning.

## Implementation Notes
- Use existing dry-run and diagnostics APIs as backend source.
- Preserve operator-grade error context in output views.

## Validation
- command: run admin UI and API integration tests
- expected output: dry-run execution and discovery exports work end-to-end

## Rollout
- Gate admin routes to internal users only for Phase 2.

## Risks
- Discovery statistics quality depends on extraction coverage.
