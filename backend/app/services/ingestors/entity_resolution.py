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
"""Entity-resolution ingestor.

Reads extracted organization names from NewsItem.extracted (Phase E output)
and resolves each via the multi-strategy resolver, writing canonical entities
and aliases to the DB. Reports new clusters + already-known hits.
"""
from __future__ import annotations

from collections import Counter

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.orm import Entity, EntityAlias, NewsItem
from app.services.entity_resolver import KNOWN_CANONICALS, resolve
from app.services.ingestors.base import Ingestor
from app.services.pipeline_log import finish_run, start_run

log = get_logger(__name__)

# Common title-case words the fallback extractor mistakes for orgs.
# These get filtered out so the entity table stays clean.
_NOISE_ORGS = {
    "Another", "What", "The", "This", "That", "These", "Those", "When", "Where",
    "Why", "How", "Who", "Which", "While", "Where", "Apple", "Apply", "CEO",
    "AI Pro", "AI", "ML", "LLM", "TechCrunch Disrupt", "Equity podcast",
    "Executive", "Chairman", "Cook", "Ternus", "Contact", "Less",
}


def _is_noise(name: str) -> bool:
    if len(name) < 2:
        return True
    if name in _NOISE_ORGS:
        return True
    # Single all-caps acronyms (1-3 letters) are usually not orgs
    if name.isupper() and len(name) <= 3 and name not in {"AWS", "IBM", "SAP"}:
        return True
    return False


class EntityResolutionIngestor(Ingestor):
    name = "entity_resolution"
    module = "entities"
    source = "Seed dict + fuzzy + DB"

    async def run(self, session: AsyncSession) -> dict:
        run = await start_run(session, self.module, self.source)
        resolved = 0
        new_entities = 0
        new_aliases = 0
        failed = 0

        try:
            items = (
                await session.execute(
                    select(NewsItem).where(NewsItem.extracted.isnot(None)).limit(500)
                )
            ).scalars().all()

            seen_in_this_run: dict[str, str] = {}

            for n in items:
                ex = n.extracted or {}
                orgs = ex.get("organizations") or []
                for o in orgs:
                    if not isinstance(o, dict):
                        continue
                    raw = (o.get("name") or "").strip()
                    if not raw or len(raw) < 2 or _is_noise(raw):
                        continue
                    try:
                        result = await resolve(raw, kind="company", db_session=session)
                    except Exception as e:
                        log.warning("resolve failed for %r: %s", raw, e)
                        failed += 1
                        continue

                    canonical = result.canonical
                    if not canonical:
                        failed += 1
                        continue

                    if canonical in seen_in_this_run:
                        resolved += 1
                        continue

                    ent = (
                        await session.execute(
                            select(Entity).where(Entity.kind == "company", Entity.canonical == canonical)
                        )
                    ).scalar_one_or_none()

                    if ent is None:
                        ent = Entity(kind="company", canonical=canonical, confidence=result.confidence)
                        session.add(ent)
                        await session.flush()
                        new_entities += 1

                    if raw.lower() != canonical.lower():
                        alias_norm = raw.lower()
                        existing_alias = (
                            await session.execute(
                                select(EntityAlias).where(
                                    EntityAlias.kind == "company",
                                    EntityAlias.alias == alias_norm,
                                )
                            )
                        ).scalar_one_or_none()
                        if existing_alias is None:
                            session.add(
                                EntityAlias(
                                    entity_id=ent.id,
                                    alias=alias_norm,
                                    kind="company",
                                    confidence=result.confidence,
                                    reasoning=f"{result.method}: {result.reasoning}",
                                )
                            )
                            new_aliases += 1

                    seen_in_this_run[canonical] = result.method
                    resolved += 1

            await session.flush()
            await finish_run(
                session, run, status="success",
                fetched=len(items), new=new_entities, updated=new_aliases, failed=failed,
                message=f"resolved={resolved} new_entities={new_entities} new_aliases={new_aliases}",
            )
            await session.commit()
            log.info("entity resolution: resolved=%d new_entities=%d new_aliases=%d",
                     resolved, new_entities, new_aliases)
        except Exception as e:
            log.exception("entity resolution failed")
            await finish_run(session, run, status="failed", fetched=0, new=0, updated=0,
                             failed=failed + 1, message=str(e))
            await session.commit()
            raise

        return {
            "fetched": len(items),
            "resolved": resolved,
            "new_entities": new_entities,
            "new_aliases": new_aliases,
            "failed": failed,
        }
