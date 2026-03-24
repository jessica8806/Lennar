# jessica8806 — Monorepo

This repository contains two independent projects that share a single git repo for now.

---

## Projects

### Lennar Land Acquisition — AI Workflow Skills

AI-assisted workflow tools for Lennar's land acquisition and finance teams. Claude skills (slash commands) that accelerate comp normalization, entitlement research, scenario modeling, offer memo drafting, and forecast narrative.

**Root files:**
```
CLAUDE.md                   Project context, loaded automatically by Claude Code
.claude/commands/           Claude skills — invoke with /skill-name
land-acquisition/           Deal data, normalized comps, models, offers
```

**Skills:** `/xls` `/normalize-comps` `/entitlement-summary` `/scenario-model` `/offer-memo` `/forecast-narrative`

See [CLAUDE.md](./CLAUDE.md) for full context, terminology, and skill reference.

---

### CivicSignal — Municipal Meeting Intelligence

Municipal meeting intelligence platform. Tracks city/county planning signals from Granicus and Legistar sources.

**Root files:**
```
civicsignal/
  src/civicsignal/          Python backend and connectors
  tests/                    Test suite
  docs/                     PRD, architecture, roadmap, task docs
  api/                      Vercel serverless entry point
  pyproject.toml            Package config
  requirements.txt          Dependencies
  vercel.json               Vercel deployment config
```

**Dev setup:**
```bash
cd civicsignal
pip install -r requirements.txt
python -m civicsignal
```

---

## Repo Notes

- `.claude/commands/` stays at the repo root — Claude Code requires it there to load skills
- `.github/` stays at root — GitHub requires it there for issue templates
- These two projects will likely move to separate repos once the Lennar project is further along
