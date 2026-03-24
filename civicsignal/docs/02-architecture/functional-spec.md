# CivicSignal Functional Specification (Engineering)

This document captures **system behavior and implementation requirements** (how the platform works technically).

## System Components
1. Scraper System
2. Document Processing Pipeline
3. Signal Detection Engine
4. Data Storage
5. Front-End Interface

## Architecture Overview
Scheduler
→ City Registry
→ Connector Router
→ Platform Connector
→ Meeting Parser
→ Document Downloader
→ Text Extraction
→ Signal Engine
→ Database
→ Front-End UI

## Platform Connectors
Required connector types:
- Granicus
- Legistar
- Laserfiche
- NovusAGENDA
- Hyland OnBase
- CivicPlus

Connector contract reference:
- `docs/02-architecture/connector-interface-spec.md`

Each connector must implement:
- meeting discovery
- agenda parsing
- document extraction

## City Connector Map (Phase 1)
| City | Platform |
|---|---|
| Irvine | Granicus |
| Anaheim | Granicus |
| Santa Ana | Laserfiche |
| Huntington Beach | Legistar |
| Newport Beach | Legistar |
| Costa Mesa | Legistar |
| Fullerton | Legistar |
| Garden Grove | NovusAGENDA |
| Mission Viejo | OnBase |
| Laguna Niguel | CivicPlus |

## Meeting Discovery Requirements
For each discovered meeting, extract:
- meeting_date
- meeting_title
- meeting_body
- agenda_url
- minutes_url
- video_url

## Document Ingestion Requirements
Download and process:
- agenda
- agenda packets
- staff reports

Constraint:
- skip files > 25 MB

## Document Storage
Object storage path format:
`/city/body/year/meeting_id/document_id.pdf`

Example:
`/irvine/city_council/2026/2026-02-25/agenda_packet.pdf`

## Document Processing Pipeline
Download
→ File hash
→ Text extraction
→ Chunking
→ Vector index
→ Signal extraction

OCR policy:
- OCR fallback only when direct text extraction is unavailable

## Change Detection
Use document/page hashing to track:
- agenda updates
- agenda item changes
- document replacements

## Signal Extraction
Signal detection combines:
- keyword rules
- document context
- LLM classification

Rules:
- one agenda item may produce multiple signals
- each signal requires one primary category
- summary generation must follow source precedence:
	1. staff report text
	2. agenda packet text
	3. agenda item description
	4. title-only fallback
- if only title-level content is available, summary must be explicitly labeled `Title-only: <title>` and confidence must be `Low`
- content-availability checks must reject boilerplate-only text as summary source

## Signal Object Schema
- signal_id
- city
- meeting_body
- meeting_date
- agenda_item_number
- signal_category
- signal_type
- title
- summary
- summary_source
- content_available
- confidence
- project_entity_id
- supporting_documents
- source_urls
- extraction_notes
- created_at

Signal summary semantics:
- `summary` may be title-only fallback when richer text is unavailable.
- `summary_source` enum: `staff_report`, `agenda_packet`, `item_description`, `title_only`.
- `content_available=false` indicates summary was generated without meaningful body text.
- `extraction_notes` should explain fallback/quality gate decisions.

## Project Entity Grouping
Group related signals by:
- agenda title similarity
- developer name
- project name
- address match

## Database Schema
### Cities
- city_id
- city_name
- state
- platform_type

### Bodies
- body_id
- city_id
- body_name
- calendar_url
- connector_type

### Meetings
- meeting_id
- city_id
- body_id
- meeting_date
- meeting_title
- source_url

### Documents
- document_id
- meeting_id
- document_type
- file_url
- file_hash
- storage_uri

### Agenda Items
- agenda_item_id
- meeting_id
- item_number
- title
- summary

### Signals
- signal_id
- city_id
- meeting_id
- agenda_item_id
- signal_category
- signal_type
- confidence
- project_entity_id

### Project Entities
- project_entity_id
- project_name
- first_detected_date
- latest_activity_date

## Scheduler Behavior
Cadence:
- daily

Per run:
- check new meetings
- detect updates
- download documents
- reprocess changed documents

## Front-End Requirements
Navigation:
- Dashboard
- Signals
- Meetings
- Documents
- Search
- Cities (Admin)
- Taxonomy (Admin)
- System Health

### Signals Page
Columns:
- Date
- City
- Body
- Signal Type
- Project
- Confidence
- Documents

Filters:
- City
- Category
- Date
- Confidence
- Keyword

### Meetings Page
Must display:
- agenda
- agenda items
- documents
- signals detected

### Document Library
Search/filter fields:
- city
- date
- document type
- keywords

### System Health
Must display:
- last scrape per city
- documents downloaded
- errors
- connector status

### Signal Discovery Mode
Admin mode for taxonomy tuning with:
- top agenda phrases
- top staff report phrases
- frequent entities
- common bigrams/trigrams

## Phase 1 Scale Assumptions
- 10 cities
- ~480 meetings
- ~3,000 documents
