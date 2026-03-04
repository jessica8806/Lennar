# Roadmap

## Execution Start Readiness
- Status: Ready to start immediately after sign-off on PRD + functional spec
- Recommended start: Now (engineering kickoff can begin in current sprint)

## Week 1 — Scraper Framework + Connectors
- Implement scheduler, city registry, connector router
- Build connector interfaces and initial platform adapters
- Add connector map for 10 phase-1 cities

## Week 2 — Ingestion + Storage
- Implement meeting parsing and document download pipeline
- Add hash-based dedupe and storage path conventions
- Enforce document type and size constraints

## Week 3 — Text + Indexing
- Implement PDF extraction and OCR fallback
- Add chunking and vector indexing
- Validate extraction quality on sample city sets

## Week 4 — Signal Engine + Grouping
- Build signal extraction and category classification
- Implement one-to-many signal creation per agenda item
- Add project entity grouping heuristics

## Week 5 — UI + Dashboards
- Ship Dashboard, Signals, Meetings, Documents, Search pages
- Add admin views: Cities, Taxonomy, System Health
- Implement update indicators for changed documents/agendas

## Week 6 — Backfill + Hardening
- Run 12-month historical ingestion
- Validate connector reliability and error handling
- Ship connector test harness and operational runbook