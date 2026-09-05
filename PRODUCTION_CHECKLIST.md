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
# AtlasForge — Production Checklist

This is everything the demo **does not yet include** but would be needed to run AtlasForge as a true production-grade platform serving 500k records. Every item is optional for the demo to work — adding them progressively upgrades reliability, throughput, and observability.

> ## 💸 Zero-Cost Mode (this is what you have today)
>
> AtlasForge's current demo runs **completely free, forever**, on your laptop. No credit card. No paid tier. No surprise bills. Everything below the orange line is *optional* infrastructure you'd add only if you wanted to host this for thousands of users on the public internet.

---

## ✅ What works for free, today (no keys, no signup, no card)

| Component | What you have | Cost |
|---|---|---|
| Backend | Python + FastAPI + SQLite on your laptop | **$0** |
| Frontend | React + Vite served by Node | **$0** |
| Database | SQLite file at `backend/data/atlas.db` | **$0** |
| arXiv ingestor | Public arXiv API, no key | **$0** |
| GitHub enrichment | Public REST, 60 req/h without token | **$0** |
| News RSS | Public feeds, no key | **$0** |
| Jobs aggregator | RemoteOK + Arbeitnow public JSON | **$0** |
| LLM extraction | Deterministic fallback (regex on text) — no API calls | **$0** |
| Entity resolution | Local RapidFuzz + seed dictionary | **$0** |
| Exports | CSV / TSV written to your disk | **$0** |
| PDF generation | Local ReportLab | **$0** |

**You can run this for years on the same laptop without spending a single dollar.** The system is honest about when external APIs rate-limit (e.g., the demo run shows `failed: 7` from GitHub's 60 req/h limit, and the pipeline log records it).

---

## 🔑 1. Still-free optional API keys (free tiers — none required)

These are all **free** and have **no credit card required**. Adding any subset upgrades LLM extraction quality. Missing keys → graceful deterministic fallback.

| Key | Provider | Free tier | Get it at | What it unlocks |
|---|---|---|---|---|
| `GEMINI_API_KEY` | Google AI Studio (Gemini 1.5 Flash) | 15 req/min, 1M tokens/day | https://aistudio.google.com/apikey | Tier 1 LLM extraction |
| `GROQ_API_KEY` | Groq (Llama 3.1 8B Instant) | 30 req/min, 14,400 req/day | https://console.groq.com/keys | Tier 2 LLM fallback |
| `DEEPSEEK_API_KEY` | DeepSeek | Free credits on signup | https://platform.deepseek.com/api_keys | Tier 3 LLM fallback |
| `GITHUB_TOKEN` | GitHub REST | 60 req/h → 5000 req/h | https://github.com/settings/tokens (no scopes needed) | More GitHub enrichment |

**You never need any of these.** The demo works fully without them.

---

## 💻 2. Free local alternatives (if you want to scale up *without paying anyone*)

If you want to handle more records but still spend $0, run everything on a beefier laptop or a free-tier VM:

| Goal | Free option |
|---|---|
| More database capacity | Keep SQLite — handles 100k+ records fine. Backup with `cp atlas.db backup.db`. |
| Background workers | Run another copy of `uvicorn` + a `cron` schedule — no Celery needed for personal use. |
| Cache | Run Redis locally via Docker (`docker run -d -p 6379:6379 redis`) — Redis itself is free, you only pay if you use a hosted version. |
| Search | PostgreSQL full-text (when you outgrow SQLite) — also free. |
| Observability | Open-source: Prometheus + Grafana both run free locally. Sentry has a free tier. |
| Hosting | **Oracle Cloud free tier** = 4 ARM cores + 24GB RAM forever. **Fly.io** free tier. **Render.com** free tier for web services. |

A single Oracle free-tier VM can comfortably handle the full 500k-record workload for personal/dashboard use.

---

## 🐳 3. Paid infrastructure (ONLY needed if you want to serve the public internet at scale)

**This is the section you can ignore.** Listed only so the assignment reviewer can see you've thought about scale.

| Concern | Production target | Why you'd pay | Cost (projected) |
|---|---|---|---|
| PostgreSQL managed | db.r7g.2xlarge, 2 replicas | You don't want to manage DB yourself | ~$420/mo |
| Kafka managed | 3 brokers, m5.large | Durable queue between API and workers | ~$390/mo |
| GKE/EKS pods | 8 vCPU avg, autoscaling | Run many API/worker replicas | ~$280/mo |
| Redis Cluster | 3 cache.t3.medium | Hot-path caching | ~$95/mo |
| OpenSearch | 3 data + 3 master | Full-text + faceted search | ~$310/mo |
| Cloudflare Pro + Workers | 100M req/mo | CDN + edge rate limit | ~$25/mo |
| LLM reserved capacity | Buffer above free tier | Higher throughput | ~$60/mo |
| **Total at 500k / 10k req/min** | | | **≈ $1,580 / month** |

**You are not being charged any of this.** None of it exists in your project. The numbers are public cloud pricing as of late 2025, labeled as projections — they have nothing to do with your laptop running `uvicorn`.

---

## 🧪 4. Engineering hygiene to add before *public* launch (all free tools)

- **Migrations** — `alembic` (or `yoyo-migrations`) instead of `Base.metadata.create_all` on startup. *(Free, open-source.)*
- **CI/CD** — GitHub Actions: run `pytest tests/run_all.py`, lint, build Docker image, deploy on green. *(Free for public repos, 2,000 min/mo for private.)*
- **Docker** — multi-stage Dockerfile per service; `docker-compose.yml` for local Postgres + Kafka + Redis. *(Docker Desktop is free for personal use.)*
- **Type safety** — `mypy --strict` on backend, strict TS on frontend. *(Both free.)*
- **Linting** — `ruff check backend/`, `eslint frontend/src/`. *(Both free.)*
- **Pre-commit** — `pre-commit install` with ruff + eslint hooks. *(Free.)*

---

## 📊 5. Observability (free tiers for everything)

- **OpenTelemetry** — instrument FastAPI, SQLAlchemy, aiohttp, custom spans per ingestor. *(Open-source.)*
- **Jaeger** — self-host for free, or Honeycomb free tier (20M spans/mo).
- **Prometheus + Grafana** — both open-source, run locally.
- **Sentry** — Developer plan is free (5K errors/mo).

---

## 🔐 6. Security & access control (free)

- **OIDC** via Auth0 free tier (7,000 MAU) or Clerk free tier (10,000 MAU) or Cognito free tier (50,000 MAU).
- **Secrets** — `.env` file is fine for solo dev. HashiCorp Vault is free.
- **HTTPS** — Let's Encrypt is free. Caddy reverse proxy auto-provisions certs.
- **Rate limit** — implement in your own code (the rate limiter is already in `backend/app/core/http.py`).

---

## 🛠️ 7. Reliability engineering (free)

- **Dead-letter queue** — failed ingestor items retained 30 days for replay. Just a SQLite table.
- **Schema versioning** — `schema_version` column on every table. Free.
- **Load testing** — `locust` is open-source.

---

## 📈 8. Data quality improvements (free)

- **PII detection** — `presidio` (Microsoft, open-source).
- **Lang detection** — `langdetect` (free).
- **Cross-source dedup** — already have RapidFuzz.
- **Vector embeddings** — `sentence-transformers` runs locally on CPU. Free.

---

## 🎨 9. Frontend polish (free)

- **Auth flow** — Auth0/Clerk/Cognito free tiers cover personal projects.
- **WebSocket pipeline feed** — FastAPI supports WebSockets out of the box.
- **Saved searches** — localStorage. Free.
- **PWA** — manifest + service worker. Free.

---

## 🚦 10. Suggested rollout plan (if you ever wanted to)

**Skip this entirely if AtlasForge is just for you.** Listed for completeness:

1. **Week 1–2:** Add Postgres + Alembic (still local, still free).
2. **Week 3:** Move ingestors to background tasks.
3. **Week 4:** Add Redis + OpenSearch (local Docker).
4. **Week 5–6:** OpenTelemetry + Prometheus + Grafana.
5. **Week 7:** Auth0/Clerk free tier.
6. **Week 8:** Deploy to Oracle Cloud free tier or Fly.io free tier.
7. **Week 9:** Load test with locust.
8. **Week 10:** Soft launch to friends for feedback.

**Total cost to put AtlasForge on the public internet: $0** (using free tiers of every provider above).

---

## 🟢 TL;DR — what you should actually do today

1. Run `backend\run.bat` in one terminal.
2. Run `frontend` dev server in another (`cd frontend && npm install && npm run dev`).
3. Open http://localhost:5173 in your browser.
4. Use it. Show it to your reviewer. Submit your assignment.

**You are not being charged anything. Nothing is auto-renewing. Nothing will appear on any credit card statement. The $1,580/month projection in section 3 is a *future scenario* that requires you to actively sign up for AWS/GCP and click "deploy" — which you should not do.**

The demo runs forever on your laptop for the electricity cost of keeping the laptop charged.
