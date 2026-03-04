# Tasks

Use one markdown file per task named:

`YYYY-MM-DD-short-title.md`

## Required fields

```md
# Task: <title>

## Linked docs
- PRD section(s):
- Architecture section(s):
- ADR(s):
- Roadmap milestone:

## Scope
-

## Acceptance Criteria
- [ ]

## Implementation Notes
-

## Validation
- command:
- expected output:

## Rollout
-

## Risks
-
```

## Initial Phase-1 backlog
1. Implement connector interface and adapter registry
2. Build Granicus and Legistar connectors first (highest city coverage)
3. Add change detection with page/doc hashes
4. Implement signal schema and confidence scoring
5. Build system health and connector dry-run harness
