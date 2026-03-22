# Lennar Land Acquisition — Project Context

This project contains AI workflow skills for Lennar's land acquisition and finance teams. All skills in this project should operate within the context defined below.

---

## Company Context

**Lennar Corporation** is one of the largest national homebuilders in the United States. This project supports two internal teams:

- **Land Acquisition**: Evaluates, underwrites, and structures offers for raw land and entitled lots
- **Finance / Land Development**: Manages budgets, forecasts, and reporting after land is acquired

---

## Terminology

Use these terms consistently across all outputs:

| Term | Meaning |
|------|---------|
| Home site | An individual lot within a community (not "lot" in formal outputs) |
| Entitlements | City/county approvals defining what can be built on a parcel |
| Underwriting | Financial analysis of a deal prior to offer submission |
| Proforma | The financial model projecting revenues, costs, and returns |
| Tranches | Phased land closing installments |
| Product type | Home design category (SFD = Single Family Detached, SFA = Single Family Attached, TH = Townhome) |
| ASP | Average Sale Price — the expected average home sale price for a community |
| Pace | Sales velocity, measured in homes sold per month |
| Community | A single Lennar development project (equivalent to a subdivision) |
| Division | Lennar's regional operating unit |
| IC | Investment Committee — the internal body that approves land purchases |
| Offer memo | Internal document submitted to IC recommending a land purchase |
| Comp | Comparable sale — a recently sold home used for market benchmarking |
| Resale | An existing home sale (not new construction) used as a comp |

---

## Deal Stages

Land acquisition deals move through these stages in order:

1. **Identification** — Parcel identified, initial data gathered
2. **Feasibility** — Preliminary underwriting, entitlement research
3. **LOI** — Letter of Intent submitted to seller
4. **Due Diligence** — Deep underwriting, site plan, consultant engagement
5. **IC Approval** — Offer memo submitted, Investment Committee votes
6. **Under Contract** — PSA executed, closing timeline confirmed
7. **Closed** — Land acquired, development begins

---

## Output Standards

All skill outputs must follow these standards:

- **File names**: Use underscores not spaces. Include date in YYYYMMDD format when relevant.
- **Tone**: Professional, direct, internal audience. Not seller-facing language.
- **Numbers**: No $ symbols in data cells. No commas in numeric fields. Decimals for percentages.
- **Dates**: MM/DD/YYYY format throughout.
- **Headings**: Title case for section headers.
- **Recommendations**: Always include a clear recommendation with supporting rationale. Do not leave decisions ambiguous.

---

## Data Sources (To Be Confirmed with Lennar Team)

> Placeholder — update after discovery session with the land team.
> Expected sources include some combination of: CoStar, Metrostudy, MLS exports, broker comp packages, internal deal database.

---

## Available Skills

| Skill | Invoke with | Purpose |
|-------|-------------|---------|
| Normalize Comp Data | `/normalize-comps` | Maps raw comp data from any source to the standard schema |
| Entitlement Summary | `/entitlement-summary` | Extracts density, setbacks, and entitlement path from zoning docs |
| Scenario Modeling | `/scenario-model` | Compares product scenarios and quantifies trade-offs |
| Offer Memo | `/offer-memo` | Drafts an IC-ready offer memo from deal inputs |
| Forecast Narrative | `/forecast-narrative` | Converts 5-year model numbers into executive commentary |

---

## Project Structure

```
land-acquisition/
  data/
    raw/        # Unprocessed comp reports, broker packages, MLS exports
    normalized/ # Standardized comp data after /normalize-comps
  models/       # Proforma models and scenario outputs
  entitlement/  # Zoning research and entitlement summaries
  offers/       # Offer memos and IC submissions
.claude/
  commands/     # Claude skill definitions (slash commands)
```
