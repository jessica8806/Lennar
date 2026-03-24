# Roadmap

## Execution Start Readiness
- Status: Ready to start immediately after sign-off on PRD + functional spec
- Recommended start: Now (engineering kickoff can begin in current sprint)

## Phase A — Platform Foundations
- Implement scheduler, city registry, connector router
- Build connector interfaces and initial platform adapters
- Add connector map for 10 phase-1 cities

## Phase B — Ingestion + Storage
- Implement meeting parsing and document download pipeline
- Add hash-based dedupe and storage path conventions
- Enforce document type and size constraints

## Phase C — Text + Indexing
- Implement PDF extraction and OCR fallback
- Add chunking and vector indexing
- Validate extraction quality on sample city sets

## Phase D — Signal Engine + Grouping
- Build signal extraction and category classification
- Implement one-to-many signal creation per agenda item
- Add project entity grouping heuristics

## Phase E — UI + Dashboards
- Ship Dashboard, Signals, Meetings, Documents, Search pages
- Add admin views: Cities, Taxonomy, System Health
- Implement update indicators for changed documents/agendas

## Phase F — Backfill + Hardening
- Run 12-month historical ingestion
- Validate connector reliability and error handling
- Ship connector test harness and operational runbook

## Phase G — Product Surface (Phase 2)
- Implement user-facing UI modules (Dashboard, Signals, Projects, Meetings, Documents, Search)
- Implement API read surfaces for signals/projects/meetings/documents
- Implement admin modules for system health, connector dry-run, and signal discovery mode
- Add UX quality indicators for summary source and content availability

Phase 2 references:
- Product definition: `docs/01-product/phase2-definition.md`
- Functional spec: `docs/02-architecture/phase2-functional-spec.md`