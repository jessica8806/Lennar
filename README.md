# CivicSignal

Municipal meeting intelligence platform for discovering, parsing, and classifying actionable government signals from Orange County city meetings.

## What this repo contains

This repository is organized in a documentation-first structure to support product clarity, architecture decisions, and execution discipline:

- `docs/00-context` — vision and constraints
- `docs/01-product` — user requirements (PRD)
- `docs/02-architecture` — system architecture, functional spec, connector registry, and ADRs
- `docs/03-execution` — roadmap and task planning
- `docs/04-operations` — runbooks and operational procedures
- `docs/05-metrics` — KPI definitions and targets

## Phase 1 scope

- Geography: 10 Orange County cities
- Bodies: City Council + Planning Commission
- Cadence: daily refresh
- Backfill: 12 months
- Document scope: agenda, agenda packets, staff reports (<= 25 MB)

## Build principles

- Use connector templates (platform-driven), not city-specific scrapers
- Keep ingestion idempotent via hashing + change detection
- Extract multiple signals per agenda item when needed
- Group signal history into project entities over time
- Make system health and connector quality visible by default
