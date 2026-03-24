# Task: Add change detection with page/document hashes

## Linked docs
- PRD section(s): Monitor changes
- Architecture section(s): System Overview -> Change Detection, Functional Spec -> Change Detection
- ADR(s): docs/02-architecture/adr/0001-template.md
- Roadmap milestone: Phase B — Ingestion + Storage

## Scope
- Compute deterministic hashes for discovered meeting pages and downloaded documents.
- Persist prior hash snapshots and compare on subsequent runs.
- Emit change events for agenda updates, agenda item changes, packet replacements, and attachment updates.
- Expose change flags for UI consumption ("Updated since last scrape").

## Acceptance Criteria
- [ ] Document hash is computed and stored for each ingested file under size limits.
- [ ] Page/content hash is computed for meeting-level change detection.
- [ ] Delta logic correctly labels new, unchanged, and changed artifacts.
- [ ] Reprocessing triggers only for changed artifacts.
- [ ] Change event schema is documented and consumable by UI/API layers.

## Implementation Notes
- Use canonicalization before hashing where appropriate to reduce false positives.
- Keep hashing independent from storage backend details.
- Include idempotency protections for reruns.

## Validation
- command: run two consecutive ingestion passes on fixed fixtures with controlled content updates
- expected output: first pass emits new; second pass emits only simulated changes with accurate event types

## Rollout
- Start in shadow mode (emit/log only), then gate reprocessing decisions after confidence check.

## Risks
- Overly sensitive hashing may create noisy updates.
- Under-sensitive hashing may miss meaningful content changes.