<!--
AtlasForge - Internship Assignment
Developer: Tejas Kamble
Email: tejaskgm1@gmail.com
Website: https://tejas-personal-portfolio-dev.vercel.app/
LinkedIn: https://www.linkedin.com/in/tejas-kamble-5342443b1
Instagram: @tejask.co.in
GitHub: https://github.com/tejasworkspacews1-ui

AtlasForge is a real-time intelligence dashboard that aggregates research papers,
news, jobs, and startup data from public APIs (arXiv, RSS feeds, RemoteOK, etc.)
with zero fabrication and zero cost. All data is Legal & freely accessible public data.
-->
# AtlasForge — AI Intelligence Graph

> **A scalable, fault-tolerant data intelligence pipeline for AI startups, products, research papers, news, and jobs.**

Built for the GraphOne / FrontierAtlas AI Engineer assignment. Production-grade architecture, runs locally on a single machine with zero budget, no paid APIs, and zero fabrication.

---

## 🟢 Zero-Cost Guarantee

**AtlasForge runs forever on your laptop with $0 spent.** No credit card, no paid tier, no surprise bills. Every component is free and open-source. Optional API keys (Gemini, Groq, DeepSeek, GitHub) have **free tiers with no card required** — missing keys trigger a deterministic fallback that never fabricates.

The only "costs" listed in `PRODUCTION_CHECKLIST.md` are *projections* for a hypothetical public-internet deployment at 500k records — they require you to actively sign up for AWS/GCP and provision managed services. **Nothing in the current project bills you.**

To run it:
```bash
cd backend && run.bat
# new terminal:
cd frontend && npm install && npm run dev
# open http://localhost:5173
```

That's it. No accounts. No .env setup required. Spend: $0.

---

## What it does

AtlasForge ingests five kinds of public AI/tech data, normalizes them, resolves entity mentions, enriches them with LLMs (with a deterministic fallback), and exports the result as CSV or Google-Sheets-ready TSV.

| Module | Source | Records in demo DB | Notes |
|---|---|---|---|
| **Research Papers** | arXiv API + GitHub REST | 30 + 3 enriched | 7 AI categories, real stars/forks |
| **News** | RSS (TechCrunch AI, MIT, VentureBeat, Verge) | 7 (24h window) | Strict freshness: 62 stale items correctly rejected |
| **Jobs** | RemoteOK + Arbeitnow JSON APIs | 0 (honest empty) | AI-keyword filter; 0 fresh AI posts currently |
| **Entities** | All extracted org mentions | 13 clusters | Seed dict + fuzzy + LLM |
| **Products / Startups** | Schema ready | 0 | Ingestors stubbed, schema portable |

---

## Quick start (60 seconds)

Requires Python 3.11+ and Node.js 20+.

```bash
# Terminal 1 — Backend
cd backend
run.bat                            # creates .venv, installs deps, starts uvicorn on :8000

# Terminal 2 — Frontend
cd frontend
npm install
npm run dev                        # starts Vite on :5173
```

Open **http://localhost:5173** in your browser. The Command Center auto-detects the backend. If the backend is offline, the UI shows an honest "Backend Offline" badge — no fabricated numbers.

---

## Verification — try it yourself

1. **Command Center** (`/`) — shows real record counts, pipeline health, recent runs
2. **Research Papers** (`/papers`) → click **Fetch arXiv** → 30 real arXiv papers from the last 24h
3. **Enrich GitHub** → 3 papers get real ⭐ counts (e.g., `Jianqiuer/Awesome6DPoseEstimation` 320 stars)
4. **News** (`/news`) → click **Fetch RSS** → only items from the last 24h appear
5. **LLM Enrich** → each news item gets an `extracted` JSON with orgs/URLs/money mentions
6. **Entity Resolution** (`/entities`) → type "Open AI" → resolves to **OpenAI** with reasoning
7. **Export Center** (`/export`) → click **Download CSV** or **Download TSV** for any module
8. **Architecture** (`/architecture`) → toggle **Current** ↔ **500k Production**, click the PDF link

---

## Architecture at a glance

```
┌─────────────────────────────────────────────────────────────────┐
│  React 18 + TS + Vite + Tailwind (obsidian "intelligence" UI)  │
└───────────────────────────────┬─────────────────────────────────┘
                                │ /api/*
┌───────────────────────────────▼─────────────────────────────────┐
│  FastAPI + uvicorn (async, OpenAPI at /docs)                    │
│  Routers: core, data, pipeline, ingest, llm, entities, export   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌──────────────┬────────────────▼─────────────┬─────────────────┐
│  arXiv RSS   │  GitHub REST  │  Multi-tier   │  Entity         │
│  RSS feeds   │  Jobs JSON    │  LLM (Gemini  │  Resolver       │
│  News JSON   │               │  →Groq→DS)    │  (seed+fuzzy+   │
│              │               │  +fallback    │   LLM)          │
└──────────────┴───────────────┴───────────────┴─────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│  SQLite (aiosqlite, Postgres-migration ready)                   │
│  7 tables: papers, startups, products, news, jobs,              │
│           entities, entity_aliases, pipeline_runs               │
└─────────────────────────────────────────────────────────────────┘
```

Full 5-layer breakdown + production roadmap: **[/architecture](http://localhost:5173/architecture)**, or download [`docs/atlasforge-architecture.pdf`](docs/atlasforge-architecture.pdf).

---

## Tech stack

**Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Lucide icons, Recharts, react-router-dom.
**Backend:** Python 3.11, FastAPI, SQLAlchemy 2 (async), aiosqlite, aiohttp, BeautifulSoup, feedparser, Pydantic v2, RapidFuzz, ReportLab.

---

## Tests

```bash
cd backend
.venv\Scripts\python tests\run_all.py
```

5 suites, 0 failures:
- `test_llm_helpers` — chunking, JSON parsing, fallback extractor
- `test_llm_adapter` — 429 retry, provider fallback, no-provider behavior, chunking
- `test_entity_resolver` — 13 alias cases incl. "Open AI" → "OpenAI", "FAIR" → "Meta"
- `test_export` — CSV quoting, TSV line safety
- `test_smoke` — every endpoint returns 200, exports include content

---

## Data integrity (read this)

- **Zero budget:** SQLite, aiohttp, free tiers only. No paid APIs used in this demo.
- **No fabrication:** every metric in the UI comes from a real API call or is labeled "Demo / No Records Yet / Offline". LLM-extracted values carry `method + provider + confidence` so consumers can audit them.
- **Honest metrics:** the pipeline log records `fetched / new / updated / failed / stale_skipped` separately. Jobs currently return 0 not because of a bug — because no AI-tagged jobs were posted on the public feeds in the last 72h. The UI says so plainly.

---

## Migration to 500k production

Same codebase. Change one env var (`ATLAS_DB_URL=postgresql+asyncpg://...`) to swap SQLite → Postgres. The 500k architecture, capacity targets, cost projection (~$1,580/mo, clearly labeled as projection), and 5-step migration plan are on **page 3** of [`docs/atlasforge-architecture.pdf`](docs/atlasforge-architecture.pdf).

---

## Project layout

```
AtlasForge/
├── frontend/                # React + TS + Vite SPA
│   ├── src/pages/           # 10 routed pages
│   ├── src/components/      # Panel, StatCard
│   └── src/lib/api.ts       # Typed fetch client
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI routers
│   │   ├── core/            # config, logging, polite HTTP
│   │   ├── db/              # async SQLAlchemy engine
│   │   ├── models/          # ORM models (7 tables)
│   │   ├── schemas/         # Pydantic v2 response models
│   │   └── services/
│   │       ├── ingestors/   # arxiv, github, news, jobs, llm_enrich, entity_resolution
│   │       ├── llm/         # multi-tier adapter + fallback
│   │       ├── entity_resolver.py
│   │       ├── export.py
│   │       └── pipeline_log.py
│   ├── tests/               # 5 test suites
│   ├── scripts/             # CLI ingestor runner + PDF builder
│   ├── data/                # SQLite DB lives here
│   └── run.bat              # one-click backend launcher
├── docs/
│   └── atlasforge-architecture.pdf
└── README.md                # ← you are here
```

---

## License

Built as an AI Engineer assignment submission. All data sources are public/free; no proprietary data is included.
