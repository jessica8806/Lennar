# Constraints

## Business Constraints
- Phase 1 must launch with 10 Orange County cities
- Scope prioritizes actionable signals over exhaustive document coverage
- Daily refresh cadence with historical backfill of 12 months

## Technical Constraints
- Multiple platform types: Granicus, Legistar, Laserfiche, NovusAGENDA, Hyland OnBase, CivicPlus
- Source websites change frequently; scraper resilience is mandatory
- File processing limit set to 25 MB per document in Phase 1
- OCR is fallback only; prioritize direct PDF text extraction

## Team Constraints
- Development timeline targets ~6 weeks for initial end-to-end v1
- Connector template model is required to reduce long-term maintenance burden
- Quality and reliability must be observable via system health and test harnesses
