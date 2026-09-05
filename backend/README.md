<!--
AtlasForge - Internship Assignment
Developer: Tejas Kamble
Email: tejaskgm1@gmail.com
Website: https://tejas-personal-portfolio-dev.vercel.app/
LinkedIn: https://www.linkedin.com/in/tejas-kamble-5342443b1
Instagram: tejask.co.in
GitHub: https://github.com/tejasworkspacews1-ui

AtlasForge is a real-time intelligence dashboard that aggregates research papers,
news, jobs, and startup data from public APIs (arXiv, RSS feeds, RemoteOK, etc.)
with zero fabrication and zero cost. All data is freely accessible public data.
-->
# AtlasForge Backend

FastAPI + SQLite + SQLAlchemy 2 (async). Schema is Postgres-ready.

## Quick start

```bash
cd backend
run.bat
```

This creates `.venv/`, installs deps, and starts uvicorn on `http://127.0.0.1:8000`.

## Endpoints
- `GET /api/health` — health check
- `GET /api/dashboard` — total records, freshness, pipeline health
- `GET /api/{papers|startups|products|news|jobs}?page=&page_size=&q=` — paginated search
- `GET /api/pipeline/runs?module=&page=` — pipeline audit log

## Architecture
- `app/core/` — config, logging, HTTP client (aiohttp + rate limiter)
- `app/db/` — async SQLAlchemy engine + session factory
- `app/models/` — ORM models (papers, startups, products, news, jobs, entities, pipeline_runs)
- `app/schemas/` — Pydantic v2 request/response models
- `app/services/` — ingestors, metrics, search, pipeline log helpers
- `app/api/` — FastAPI routers

## Migrate to Postgres later
Change `ATLAS_DB_URL` env var to `postgresql+asyncpg://user:pass@host/db`. All models use SQLAlchemy 2 typed maps and standard column types.
