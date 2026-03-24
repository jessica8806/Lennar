# Connector Interface Specification

Defines the shared contract all platform connectors must implement.

## Interface Methods

### discoverMeetings(request)
Input:
- city_id
- city_name
- platform_type
- discovery_url
- bodies[]
- date_range { start_date, end_date }
- dry_run
- live_fetch
- timeout_seconds
- max_retries
- verify_ssl

Output:
- meetings[]
  - external_meeting_id
  - meeting_date
  - meeting_title
  - meeting_body
  - agenda_url
  - minutes_url
  - video_url
  - source_url

### parseAgenda(request)
Input:
- meeting reference
- agenda_url
- dry_run

Output:
- agenda_items[]
  - external_agenda_item_id
  - item_number
  - title
  - summary
  - action
  - vote_result

### extractDocuments(request)
Input:
- meeting reference
- agenda items (optional)
- dry_run

Output:
- documents[]
  - external_document_id
  - document_type (agenda | agenda_packet | staff_report | attachment)
  - file_url
  - file_name
  - file_size_bytes
  - linked_agenda_item_id (nullable)

## Required Behaviors
- Deterministic IDs for meetings, agenda items, and documents.
- Respect maximum file size policy (skip files larger than 25 MB).
- Preserve source URLs for every emitted entity.
- Normalize meeting body values to configured canonical names.
- Emit valid source document URLs (avoid synthetic concatenated paths that are not retrievable).
- For Legistar, prefer `View.ashx` document links when available.

## Error Contract
Connector errors must include:
- error_code
- platform_type
- city_id
- body_name
- source_url
- message
- retryable (true/false)

## Dry-Run Contract
When dry_run is true:
- Connector performs discovery/parsing.
- Connector does not persist records.
- Connector does not download document binary content.
- Connector returns summary metrics:
  - meetings_discovered
  - agenda_items_parsed
  - documents_referenced
  - errors_count
  - runtime_ms

## Router Contract
- Input: platform_type + connector request
- Output: matching connector adapter or unsupported-platform error
- Unsupported platform must return a deterministic, typed error

## Validation Expectations
- Contract tests validate required fields and enums.
- Fixture tests validate platform parser stability.
- Regression tests validate deterministic IDs for unchanged source pages.
