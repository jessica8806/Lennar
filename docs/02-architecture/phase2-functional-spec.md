# Phase 2 Functional Specification (UI + APIs)

This document defines the functional architecture for Phase 2 product surfaces.

## Scope

Phase 2 adds:
- user-facing UI modules
- API read surfaces for signals/projects/meetings/documents
- admin tooling for health, connector tests, and taxonomy refinement

## Front-End Modules

- Dashboard
- Signals list/detail
- Projects list/detail
- Meetings browser/detail
- Document library
- Search
- Admin workspace

## Navigation

Main nav:
- Dashboard
- Signals
- Projects
- Meetings
- Documents
- Search
- Admin

Admin nav:
- System Health
- Connector Tests
- Signal Discovery
- Taxonomy

## Signals UI

### Signals List

Columns:
- date
- city
- body
- signal type
- project
- confidence
- documents

Filters:
- city
- category
- confidence
- date
- keyword
- content availability

Signal quality badge mapping:
- staff_report
- agenda_packet
- item_description
- title_only (warning)

### Signal Detail

Fields:
- title
- type
- category
- confidence
- summary
- summary_source
- content_available
- meeting context
- agenda item number
- supporting docs
- source links
- classification excerpt

## Projects UI

Project detail fields:
- project name
- city
- first detected
- latest activity
- timeline of related signals

## Meetings UI

Meeting detail fields:
- meeting date
- meeting body
- agenda items
- documents
- signals detected

Actions:
- open agenda
- open staff report
- search agenda items

## Documents UI

Search targets:
- agenda items
- staff reports
- document text
- meeting titles

Filters:
- city
- meeting body
- date range
- keyword

Results:
- document title
- meeting date
- city
- snippet
- document link

## Search UX

Global search returns grouped entities:
- signals
- projects
- meetings
- documents

## Admin UX

### System Health

Must display:
- last scrape status per city
- documents downloaded
- signals generated
- connector errors
- health status (healthy/warning/failed)

Must include diagnostics:
- content availability rate
- doc parse success rate
- title-only rate
- admin action prompts when title-only rates are elevated

### Connector Tests

Supports:
- city/date selection
- dry-run execution
- run output: meetings, docs, signals, errors

### Signal Discovery

Displays:
- top title phrases
- top report phrases
- common bigrams/trigrams
- common entities

## Phase 2 API Surfaces

Signals:
- GET /signals
- GET /signals/{id}

Projects:
- GET /projects
- GET /projects/{id}

Meetings:
- GET /meetings
- GET /meetings/{id}

Documents:
- GET /documents
- GET /documents/{id}

Admin:
- GET /system-health
- POST /connector-test
- GET /signal-discovery

## Non-Functional Notes

- Keep UI indicators aligned with signal quality semantics.
- Avoid presenting title-only signals as equivalent to content-backed signals.
- Ensure admin diagnostics explicitly identify extraction bottlenecks by city/platform.
