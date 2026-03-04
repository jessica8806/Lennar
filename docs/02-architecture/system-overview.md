# System Overview

## Architecture Flow
Scheduler
→ City Registry
→ Connector Router
→ Platform Connector
→ Meeting Parser
→ Document Downloader
→ Text Extraction
→ Signal Engine
→ Database + Search Index
→ Front-End UI

## Connector Strategy
Connector templates are platform-driven, not city-specific. Each connector defines:
- meeting discovery rule
- agenda parser
- document locator

City-level configuration supplies:
- platform type
- seed URL
- tracked body names

Required connector types:
- Granicus
- Legistar
- Laserfiche
- NovusAGENDA
- Hyland OnBase
- CivicPlus

## Document Pipeline
Download
→ File hashing (dedupe)
→ Text extraction
→ Chunking
→ Vector index
→ Signal extraction

Processing policy:
- Primary: native PDF text extraction
- Fallback: OCR only when necessary
- Max file size: 25 MB
- Connector-specific note: Legistar supporting documents should use `View.ashx` endpoints when available (not synthetic `MeetingDetail.aspx/...pdf` paths)

## Change Detection
Track:
- agenda amended
- agenda item added
- agenda packet replaced
- attachment updated

Methods:
- page hash
- document hash

UI requirement:
- show "Updated since last scrape" indicator

## Core Data Model
Tables:
- Cities(city_id, city_name, state, timezone, platform_type)
- Bodies(body_id, city_id, body_name, calendar_url, connector_type)
- Meetings(meeting_id, city_id, body_id, meeting_date, meeting_title, source_url, agenda_status, last_seen_at)
- Documents(document_id, meeting_id, agenda_item_id, document_type, file_url, file_hash, storage_uri, extracted_text_uri)
- AgendaItems(agenda_item_id, meeting_id, item_number, title, summary, action, vote_result)
- Signals(signal_id, city_id, meeting_id, agenda_item_id, signal_category, signal_type, confidence, project_entity_id)
- ProjectEntities(project_entity_id, project_name, developer, first_detected_date, latest_activity_date)

## Project Entity Grouping Heuristics
Group signals by combined signals from:
- project name similarity
- developer name match
- address match
- agenda title similarity

## Signal Quality Gates
- Prefer summary text sources in order: staff report → agenda packet → agenda item description → title-only fallback.
- If content is unavailable or boilerplate-only, label summary as `Title-only: ...` and keep confidence low.
- Persist summary provenance (`summary_source`) and availability (`content_available`) for downstream UX and QA.
