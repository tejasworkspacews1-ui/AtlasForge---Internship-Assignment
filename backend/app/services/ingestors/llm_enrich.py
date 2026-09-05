"""
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
"""
"""LLM-powered enrichment ingestor.

For each news item, runs the multi-tier LLM extractor over title+summary
to surface mentioned companies/products/funding. Results are stored back on
the NewsItem row as an `extracted` JSON field. We extend the schema for that.

Uses deterministic fallback when no LLM keys are configured — never fabricates.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.orm import NewsItem
from app.services.ingestors.base import Ingestor
from app.services.llm.extractor import extract_json
from app.services.llm.fallback import extract as fallback_extract
from app.services.pipeline_log import finish_run, start_run

log = get_logger(__name__)

SCHEMA_HINT = (
    'Return JSON: {"organizations":[{"name":"...","confidence":0.0-1.0,"reason":"..."}], '
    '"products":[{"name":"...","category":"..."}], '
    '"funding":[{"amount_usd":0,"unit":"M|B","investors":["..."],"reason":"..."}]}'
)


class LLMEnrichmentIngestor(Ingestor):
    name = "llm_enrich"
    module = "news"
    source = "Multi-tier LLM"

    def __init__(self, max_items: int = 25):
        self.max_items = max_items

    async def run(self, session: AsyncSession) -> dict:
        run = await start_run(session, self.module, self.source)
        fetched = new = updated = failed = 0
        llm_hits = 0
        fallback_hits = 0

        try:
            items = (
                await session.execute(
                    select(NewsItem)
                    .order_by(NewsItem.published_at.desc().nullslast())
                    .limit(self.max_items)
                )
            ).scalars().all()
            fetched = len(items)

            for n in items:
                text = f"{n.title}\n\n{n.summary or ''}"
                if not text.strip():
                    failed += 1
                    continue

                result = await extract_json(text, SCHEMA_HINT, max_tokens=500)
                if result.ok and result.data:
                    n.extracted = {"method": "llm", "provider": result.provider, "model": result.model,
                                   "data": result.data, "attempts": result.attempts}
                    llm_hits += 1
                    updated += 1
                else:
                    fb = fallback_extract(text)
                    n.extracted = {"method": "deterministic", **fb, "llm_error": result.error}
                    fallback_hits += 1
                    updated += 1

            await session.flush()
            msg = f"llm_hits={llm_hits} fallback_hits={fallback_hits}"
            await finish_run(session, run, status="success",
                             fetched=fetched, new=new, updated=updated, failed=failed, message=msg)
            await session.commit()
            log.info("llm enrich: %d items, %s", fetched, msg)
        except Exception as e:
            log.exception("llm enrich failed")
            await finish_run(session, run, status="failed", fetched=fetched, new=new,
                             updated=updated, failed=failed, message=str(e))
            await session.commit()
            raise

        return {
            "fetched": fetched, "new": new, "updated": updated, "failed": failed,
            "llm_hits": llm_hits, "fallback_hits": fallback_hits,
        }
