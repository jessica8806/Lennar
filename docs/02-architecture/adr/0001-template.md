# ADR-0001: Use Platform Connector Templates Instead of City-Specific Scrapers

- Status: Accepted
- Date: 2026-03-04
- Deciders: Product + Engineering
- Related PRD: `docs/01-product/prd.md`

## Context
City-specific scrapers are brittle and expensive to maintain at scale. CivicSignal must support 10 initial cities and scale to hundreds/thousands while source websites evolve.

## Decision
Adopt a platform-template connector architecture where each platform implementation encapsulates shared discovery and parsing behavior. Cities provide configuration only (platform type, seed URL, bodies).

## Consequences
### Positive
- Reduces maintenance and parser duplication
- Enables faster onboarding of additional cities on existing platforms
- Encourages consistent test coverage per connector type

### Negative
- Requires upfront abstraction and connector interface design
- Edge-case city behavior may still require platform override hooks

## Alternatives Considered
1. Fully city-specific scrapers
2. Single generic HTML scraper without platform adapters
