# Lennar Land Acquisition — AI Workflow Skills

AI-assisted workflow tools for Lennar's land acquisition and finance teams. This project provides Claude skills (slash commands) that accelerate the most time-consuming parts of the land deal process — data normalization, entitlement research, scenario modeling, offer memo drafting, and forecast narrative.

---

## What's In This Repo

```
CLAUDE.md                          Project context loaded automatically by Claude
.claude/
  commands/                        Claude skills — invoke with /skill-name
    normalize-comps.md             Map raw comp data to the Lennar schema
    entitlement-summary.md         Extract density, setbacks, entitlement path from zoning docs
    scenario-model.md              Compare product scenarios and quantify trade-offs
    offer-memo.md                  Draft an IC-ready offer memo from deal inputs
    forecast-narrative.md          Convert 5-year model numbers into executive commentary
  lennar-field-schema.md           Canonical field schema used by the normalize skill
land-acquisition/
  data/raw/                        Unprocessed comp reports, broker packages, MLS exports
  data/normalized/                 Normalized comp data output
  models/                          Proforma models and scenario outputs
  entitlement/                     Zoning research and entitlement summaries
  offers/                          Offer memos and IC submissions
```

---

## Skills Quick Reference

| Skill | Command | When to Use |
|-------|---------|-------------|
| Normalize Comps | `/normalize-comps` | You have a comp report (PDF, Excel, CSV) that needs to map into the underwriting model |
| Entitlement Summary | `/entitlement-summary` | You have zoning code, staff reports, or parcel details and need a structured summary |
| Scenario Model | `/scenario-model` | You want to compare product types, lot counts, or pricing assumptions side by side |
| Offer Memo | `/offer-memo` | Underwriting is done and you need an IC-ready memo drafted |
| Forecast Narrative | `/forecast-narrative` | You have 5-year model numbers and need written commentary for leadership |

---

## Getting Started

These skills run inside [Claude Code](https://claude.ai/code). No installation required beyond having Claude Code access.

**To invoke a skill:**
```
/normalize-comps land-acquisition/data/raw/broker-package-march.pdf built_after=2018 lot_min=4000
/entitlement-summary
/offer-memo
```

**To load project context**, Claude automatically reads `CLAUDE.md` at the start of each session. This file contains the terminology glossary, deal stage definitions, and output formatting standards that all skills use.

---

## The Normalize Skill — How It Works

The most detailed skill in this project. When you run `/normalize-comps` with a file path, it:

1. Reads and inventories the source file (any format)
2. Applies analyst-specified filters (year built, lot size, price range, geography)
3. Maps every source field to the Lennar schema using `lennar-field-schema.md`
4. Assigns confidence scores (High / Medium / Low) to each mapping
5. Produces a 5-tab Excel output:
   - `Normalized_Data` — records mapped to Lennar schema column order
   - `Mapping_Log` — full audit trail with confidence scores and color coding
   - `Missing_Fields` — required fields not found in source
   - `Filtered_Out` — excluded records with filter reasons
   - `Summary` — data quality score and key stats

**Output file naming:** `Lennar_Normalized_[SourceFileName]_[YYYYMMDD].xlsx`
**Output location:** `land-acquisition/data/normalized/`

---

## Field Schema

The file `.claude/lennar-field-schema.md` is the canonical reference for the normalize skill. It defines:

- 35 fields across 5 categories (property ID, lot/land, home characteristics, sale/financial, comp analysis)
- Required vs. optional status for each field
- Known synonyms — what external sources (MLS, CoStar, broker packages) call the same field
- Common mapping ambiguities and how to resolve them
- Fields that must never be estimated or invented

**Before deploying in production**, the Lennar land team should validate:
- Any Lennar-specific fields not yet in the schema (division codes, deal IDs, underwriter IDs)
- Exact column order the Excel model expects
- Which fields are auto-calculated in the model (do not populate those)
- Source-specific synonyms from CoStar, Metrostudy, and internal deal database

---

## Terminology

All skills use Lennar-standard terminology. Key terms:

| Term | Meaning |
|------|---------|
| Home site | An individual lot (never "lot" in formal outputs) |
| ASP | Average Sale Price |
| Pace | Sales velocity in homes/month |
| Community | A single Lennar development project |
| IC | Investment Committee |
| Tranches | Phased land closing installments |
| Product type | SFD / SFA / TH |
| Comp / Resale | Comparable sale used for benchmarking |

Full glossary and deal stage definitions are in `CLAUDE.md`.

---

## Project Status

| Component | Status |
|-----------|--------|
| CLAUDE.md — project context | Complete |
| 5 core skills (scaffold) | Complete |
| normalize skill — detailed version | In review |
| lennar-field-schema.md | Complete (pending Lennar team validation) |
| Sample normalized output (examples/) | Not yet created |
| Lennar team schema validation | Pending discovery session |
| Source-specific synonym expansions | Pending (CoStar, Metrostudy, MLS) |

---

## What's Next

1. **Lennar team discovery session** — validate field schema, confirm column order, identify missing fields and data sources
2. **Save final normalize skill** — incorporate review feedback, add to `.claude/commands/`
3. **Create sample output** — `examples/sample-normalized-output.md` for few-shot quality
4. **Expand synonyms** — add CoStar, Metrostudy, MLS field names once sources are confirmed
5. **Build out remaining skills** — deepen entitlement-summary, scenario-model, offer-memo with the same level of detail as normalize
