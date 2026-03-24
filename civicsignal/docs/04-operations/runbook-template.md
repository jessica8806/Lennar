# Operations Runbook (CivicSignal)

## Service Ownership
- Product owner: CivicSignal PM
- Engineering owner: Data Platform team
- On-call channel: `#civicsignal-oncall`

## Daily Operational Checks
1. Verify last scrape timestamp for each city
2. Check connector failures and error counts
3. Confirm document ingestion and extraction throughput
4. Review low-confidence signal volume anomalies

## Alert Definitions
- `scrape_stale_city` — no successful scrape in 36h (sev2)
- `connector_error_spike` — >20% failures over rolling 24h (sev2)
- `extraction_failure_spike` — OCR/PDF extraction failures >10% (sev2)
- `indexing_lag` — signals delayed >24h from document ingestion (sev3)

## Incident Diagnosis
1. Identify impacted city/body and connector type
2. Re-run connector test harness in dry-run mode for last 30 days
3. Compare current page/doc hashes versus prior successful run
4. Validate source site availability and markup changes
5. Apply connector patch or temporary retry/backoff mitigation

## Recovery Actions
1. Backfill affected date range
2. Reprocess changed documents and signal extraction
3. Validate system health dashboard returns to green
4. Post incident summary and follow-up tasks
