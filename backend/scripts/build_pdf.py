# AtlasForge - Internship Assignment
# Developer: Tejas Kamble
# Email: tejaskgm1@gmail.com
# Website: https://tejas-personal-portfolio-dev.vercel.app/
# LinkedIn: https://www.linkedin.com/in/tejas-kamble-5342443b1
# Instagram: tejask.co.in
# GitHub: https://github.com/tejasworkspacews1-ui
#
# AtlasForge is a real-time intelligence dashboard that aggregates research papers,
# news, jobs, and startup data from public APIs (arXiv, RSS feeds, RemoteOK, etc.)
# with zero fabrication and zero cost. All data is freely accessible public data.
"""Generate the 3-page AtlasForge architecture PDF using ReportLab.

Page 1 — System overview + current architecture (5 layers)
Page 2 — Data integrity, security, observability, error handling
Page 3 — 500k-record production roadmap with cost projections (clearly labeled)
"""
from __future__ import annotations

import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

sys.path.insert(0, ".")

OUT_PATH = Path(__file__).resolve().parents[2] / "docs" / "atlasforge-architecture.pdf"
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def make_styles():
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "Title", parent=styles["Title"],
        fontName="Helvetica-Bold", fontSize=22, leading=26,
        textColor=colors.HexColor("#0a0e18"), spaceAfter=8,
    )
    h2 = ParagraphStyle(
        "H2", parent=styles["Heading2"],
        fontName="Helvetica-Bold", fontSize=13, leading=16,
        textColor=colors.HexColor("#22d3ee"), spaceBefore=10, spaceAfter=4,
    )
    h3 = ParagraphStyle(
        "H3", parent=styles["Heading3"],
        fontName="Helvetica-Bold", fontSize=11, leading=14,
        textColor=colors.HexColor("#a78bfa"), spaceBefore=6, spaceAfter=2,
    )
    body = ParagraphStyle(
        "Body", parent=styles["BodyText"],
        fontName="Helvetica", fontSize=9.5, leading=12.5,
        textColor=colors.HexColor("#1f2937"),
    )
    small = ParagraphStyle(
        "Small", parent=body,
        fontSize=8, leading=10, textColor=colors.HexColor("#475569"),
    )
    mono = ParagraphStyle(
        "Mono", parent=body,
        fontName="Courier", fontSize=8.5, leading=11,
        textColor=colors.HexColor("#0f172a"),
    )
    return {"title": title, "h2": h2, "h3": h3, "body": body, "small": small, "mono": mono}


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#94a3b8"))
    canvas.drawString(0.75 * inch, 0.5 * inch, "AtlasForge Architecture — v0.1.0")
    canvas.drawRightString(LETTER[0] - 0.75 * inch, 0.5 * inch, f"Page {doc.page} of 3")
    canvas.setStrokeColor(colors.HexColor("#22d3ee"))
    canvas.setLineWidth(0.5)
    canvas.line(0.75 * inch, 0.7 * inch, LETTER[0] - 0.75 * inch, 0.7 * inch)
    canvas.restoreState()


def make_layer_table(rows):
    t = Table(rows, colWidths=[1.6 * inch, 4.8 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0a0e18")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#22d3ee")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
        ("FONTSIZE", (0, 1), (-1, -1), 8.5),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 1), (1, -1), "Helvetica"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 1), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
    ]))
    return t


def build():
    s = make_styles()
    story = []

    # ============ PAGE 1 — System overview ============
    story.append(Paragraph("AtlasForge — AI Intelligence Graph", s["title"]))
    story.append(Paragraph("Architecture Document · v0.1.0", s["small"]))
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("System Overview", s["h2"]))
    story.append(Paragraph(
        "AtlasForge is a scalable, fault-tolerant data intelligence pipeline that collects, "
        "processes, and normalizes data about AI startups, products, research papers, news, "
        "and jobs. The current implementation runs locally on a single machine using SQLite, "
        "FastAPI, and React. Every component is designed so that swapping in PostgreSQL, "
        "Kafka, and Redis later requires zero application-code changes — only an environment "
        "variable and infrastructure provisioning.",
        s["body"]))

    story.append(Paragraph("Current Architecture (5 Layers)", s["h2"]))
    layers = [
        ["Layer", "Components"],
        ["Presentation",
         "React 18 + TypeScript + Vite · Tailwind + Lucide + Recharts · "
         "10 routed pages (Command Center, Papers, Startups, Products, News, Jobs, "
         "Entity Resolution, Pipeline Logs, Export, Architecture)"],
        ["API",
         "FastAPI + uvicorn · Pydantic v2 · CORS to :5173 · "
         "Endpoints: /health, /dashboard, /{module}, /pipeline/runs, /ingest, "
         "/llm, /entities, /export"],
        ["Ingestion",
         "6 ingestors: arXiv (Atom XML), GitHub enrichment (REST), "
         "RSS news (4 feeds), Jobs (RemoteOK + Arbeitnow JSON), "
         "LLM enrichment, Entity resolution. "
         "Per-host rate limiter (2s default)."],
        ["LLM Tier",
         "Multi-tier adapter: Gemini 1.5 Flash → Groq Llama 3.1 → DeepSeek. "
         "Exponential backoff + jitter (4 attempts, 0.8–16s). "
         "Pre-chunking for 413 payloads. "
         "Deterministic fallback (title-case, URL, email, money) — never fabricates."],
        ["Storage",
         "SQLite via aiosqlite. 7 tables: papers, startups, products, news, "
         "jobs, entities, entity_aliases, pipeline_runs. "
         "Unique (source, source_id) for dedup. JSON columns for arrays. "
         "Postgres-ready via asyncpg URL swap."],
    ]
    story.append(make_layer_table(layers))
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("Data Flow", s["h3"]))
    story.append(Paragraph(
        "Ingestor → async fetch → normalize → unique-key dedup → "
        "optional LLM extraction (with deterministic fallback) → "
        "DB write + PipelineRun audit row. "
        "Frontend polls /dashboard + /pipeline/runs every 30s. "
        "All ingestors are idempotent and re-runnable.",
        s["mono"]))

    story.append(Paragraph("Verified End-to-End (no fabrication)", s["h3"]))
    story.append(Paragraph(
        "30 real arXiv papers ingested from cs.AI/LG/CL/CV/RO/IR + stat.ML. "
        "3 papers enriched with real GitHub stars (e.g. 320★). "
        "69 RSS items fetched, 7 kept within 24h freshness, 62 rejected for staleness. "
        "13 entity clusters resolved from real news mentions. "
        "5/5 test suites pass (LLM helpers, LLM adapter, entity resolver, export, smoke).",
        s["body"]))

    story.append(PageBreak())

    # ============ PAGE 2 — Quality, integrity, ops ============
    story.append(Paragraph("Data Integrity & Honesty", s["title"]))
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("Hard Constraints", s["h2"]))
    story.append(Paragraph(
        "<b>Zero budget:</b> only free, open-source tools. SQLite, aiohttp, "
        "feedparser, RapidFuzz, ReportLab, free tiers of Gemini/Groq/DeepSeek/GitHub. "
        "No paid APIs, hosting, or databases.",
        s["body"]))
    story.append(Paragraph(
        "<b>No hallucinations:</b> every record comes from a legitimate source or is "
        "labeled 'deterministic'. LLM-extracted values carry method + provider + "
        "confidence metadata so downstream consumers can distinguish.",
        s["body"]))
    story.append(Paragraph(
        "<b>Honest metrics:</b> the dashboard distinguishes between real collected "
        "records, failed/pending records (reported separately in the pipeline log), "
        "and architectural projections (clearly labeled). The UI shows 'No Records Yet' "
        "or 'Backend Offline' rather than fabricating numbers.",
        s["body"]))

    story.append(Paragraph("Reliability & Error Handling", s["h2"]))
    story.append(Paragraph(
        "<b>Idempotent ingestors:</b> every ingestor uses (source, source_id) unique "
        "constraints so re-running cannot create duplicates — only updates existing rows.",
        s["body"]))
    story.append(Paragraph(
        "<b>Per-host rate limiter:</b> a token-bucket implemented in <font name='Courier'>core/http.py</font> "
        "enforces a minimum 2s gap between requests to the same host, with global override via "
        "<font name='Courier'>ATLAS_RATE_LIMIT</font> env var. Polite to public APIs.",
        s["body"]))
    story.append(Paragraph(
        "<b>Per-provider backoff:</b> 429 and 5xx responses from LLM providers trigger "
        "exponential backoff with 25% jitter, max 4 attempts before moving to next tier. "
        "413 payloads are pre-chunked (12k chars + overlap) and results merged as JSON arrays.",
        s["body"]))
    story.append(Paragraph(
        "<b>Pipeline audit:</b> every run writes a PipelineRun row with run_id, module, "
        "source, status, fetched/new/updated/failed counts and a free-text message. "
        "Visible at <font name='Courier'>/pipeline</font> in the UI.",
        s["body"]))

    story.append(Paragraph("Schema & Migration Posture", s["h2"]))
    schema_rows = [
        ["Decision", "Rationale"],
        ["SQLAlchemy 2 typed maps", "Same model files work with SQLite + Postgres"],
        ["JSON columns for arrays", "authors_json, categories, extracted — Postgres JSONB equivalent"],
        ["UniqueConstraint on (source, source_id)", "DB-level dedup, not app-level"],
        ["Timestamp with timezone", "All datetimes stored UTC; no naive datetime bugs"],
        ["Async everywhere", "aiosqlite → asyncpg swap is a one-env-var change"],
        ["No ORM migrations yet", "For demo: <font name='Courier'>Base.metadata.create_all</font> on startup"],
    ]
    story.append(make_layer_table(schema_rows))

    story.append(Paragraph("Observability (current)", s["h2"]))
    story.append(Paragraph(
        "<b>Structured stdout logging</b> with timestamps and module names. "
        "<b>Pipeline log</b> endpoint exposes every run with full audit. "
        "<b>Health endpoint</b> reports service version + UTC time. "
        "Production roadmap (page 3) adds OpenTelemetry traces + Prometheus metrics.",
        s["body"]))

    story.append(PageBreak())

    # ============ PAGE 3 — Production roadmap ============
    story.append(Paragraph("500k-Record Production Roadmap", s["title"]))
    story.append(Paragraph("Architecture Document · Page 3 of 3", s["small"]))
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("Capacity Targets", s["h2"]))
    cap = [
        ["Metric", "Current (Local)", "Production Target"],
        ["Records in DB", "~50 (verified)", "500,000"],
        ["Records / day ingested", "≤100", "≥10,000"],
        ["API requests / minute", "≤10", "10,000 sustained"],
        ["P95 API latency", "n/a (single user)", "≤300ms"],
        ["Uptime SLO", "n/a", "99.9% (≤8.7h/yr downtime)"],
        ["Backup retention", "none", "30-day PITR + geo-redundant"],
    ]
    story.append(make_layer_table(cap))
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("Target Architecture (6 Tiers)", s["h2"]))
    prod = [
        ["Tier", "Components"],
        ["Edge / CDN",
         "Cloudflare or Fastly · TLS + WAF · Brotli + HTTP/3 · "
         "Edge rate limit (10k req/min/IP)"],
        ["Stateless API",
         "FastAPI on GKE/EKS · HPA 3–50 pods · OIDC + per-tenant JWT · "
         "OpenTelemetry → Jaeger · Cooperative 429 backpressure"],
        ["Streaming Bus",
         "Kafka 3 brokers · topics: raw.arxiv, raw.news, raw.jobs, "
         "raw.papers.github, normalized.entities · "
         "exactly-once semantics + Avro schema registry"],
        ["Worker Tier",
         "Ingestor workers (Celery/RQ) 5–30 concurrent · "
         "LLM workers (reserved TPM + circuit breaker) · "
         "Entity resolver workers (GPU-free) · DLQ 30-day retention"],
        ["Cache + Search",
         "Redis Cluster (hot reads, dedup) · "
         "OpenSearch 3 shards (full-text, facets) · "
         "Qdrant (vector store for semantic dedup)"],
        ["Storage",
         "PostgreSQL 16 primary + 2 replicas · pgvector + JSONB GIN · "
         "Sharded by source_id hash · S3/GCS cold storage · PITR 30d"],
    ]
    story.append(make_layer_table(prod))
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("Cost Projection (clearly labeled)", s["h2"]))
    story.append(Paragraph(
        "<b>This is an architectural projection, not actual spend.</b> "
        "Based on public cloud pricing as of late 2025. Actual costs depend on "
        "egress, storage growth, and LLM token usage.",
        s["small"]))
    cost = [
        ["Component", "Spec", "Monthly (USD)"],
        ["PostgreSQL (managed)", "db.r7g.2xlarge, 500GB, 2 replicas", "$420"],
        ["Kafka (managed)", "3 brokers, m5.large, 1TB", "$390"],
        ["GKE pods (API + workers)", "8 vCPU avg, autoscaling", "$280"],
        ["Redis Cluster", "3 nodes, cache.t3.medium", "$95"],
        ["OpenSearch", "3 data + 3 master, t3.medium", "$310"],
        ["Cloudflare Pro + Workers", "100M requests/mo", "$25"],
        ["LLM reserved capacity", "Gemini + Groq + DeepSeek free + buffer", "$60"],
        ["Observability", "Honeycomb + Grafana Cloud free tiers", "$0"],
        ["TOTAL (projected)", "", "≈ $1,580 / month"],
    ]
    story.append(make_layer_table(cost))
    story.append(Spacer(1, 0.1 * inch))

    story.append(Paragraph("Migration Steps (incremental)", s["h2"]))
    story.append(Paragraph(
        "1. <b>Storage swap:</b> set <font name='Courier'>ATLAS_DB_URL=postgresql+asyncpg://…</font> "
        "and re-run. No code changes — SQLAlchemy maps the existing models.",
        s["body"]))
    story.append(Paragraph(
        "2. <b>Async worker offload:</b> add a Celery/RQ layer. Move ingestors into tasks. "
        "API endpoints switch from <i>await ingestor.run()</i> to <i>task.delay()</i>.",
        s["body"]))
    story.append(Paragraph(
        "3. <b>Kafka between API and workers:</b> topics become the durability boundary. "
        "API only publishes; workers consume + dedup.",
        s["body"]))
    story.append(Paragraph(
        "4. <b>Read replicas + Redis:</b> add pgBouncer in front, Redis for hot-path "
        "dashboard counters, OpenSearch for full-text.",
        s["body"]))
    story.append(Paragraph(
        "5. <b>Observability:</b> instrument with OpenTelemetry, export to Jaeger/Honeycomb. "
        "Add Prometheus + Grafana for SLO dashboards.",
        s["body"]))

    story.append(Paragraph("Risks & Mitigations", s["h2"]))
    story.append(Paragraph(
        "<b>Free-tier LLM rate limits</b> — mitigated by multi-tier fallback and "
        "respectful per-provider budgeting. <br/>"
        "<b>Public RSS feed reliability</b> — mitigated by per-feed failure isolation; "
        "2 of 4 feeds failed during the demo run and were honestly logged. <br/>"
        "<b>Entity resolution correctness</b> — mitigated by always returning "
        "<i>method + confidence + reasoning</i> so downstream consumers can reject low-confidence matches. <br/>"
        "<b>Schema drift during migration</b> — mitigated by SQLAlchemy typed maps + "
        "JSON columns for arrays, validated by the existing test suite.",
        s["body"]))

    doc = SimpleDocTemplate(
        str(OUT_PATH), pagesize=LETTER,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
        title="AtlasForge Architecture",
        author="AtlasForge Team",
    )
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(f"Wrote {OUT_PATH}")
    print(f"Size: {OUT_PATH.stat().st_size:,} bytes")


if __name__ == "__main__":
    build()
