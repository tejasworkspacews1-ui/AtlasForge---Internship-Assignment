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
"""Papers-with-Code style enrichment: attach GitHub repo stats to arXiv papers.

Uses GitHub's free REST API to search repositories that reference each arXiv id,
then picks the highest-star match. Caches results on the Paper row.

Rate limits: 60 req/h unauthenticated, 5000/h with GITHUB_TOKEN.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.http import _rate_limiter, http_session
from app.core.logging import get_logger
from app.models.orm import Paper
from app.services.github_client import GitHubClient
from app.services.ingestors.base import Ingestor
from app.services.pipeline_log import finish_run, start_run

log = get_logger(__name__)

GITHUB_SEARCH = "https://api.github.com/search/repositories"


def _parse_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


class GitHubEnrichmentIngestor(Ingestor):
    name = "github_enrichment"
    module = "papers"
    source = "GitHub API"

    def __init__(self, max_papers: int = 20, token: str | None = None):
        self.max_papers = max_papers
        self.gh = GitHubClient(token=token)

    async def _search_best_repo(self, session, arxiv_id: str) -> dict | None:
        from urllib.parse import quote_plus
        q = f"{arxiv_id} in:readme"
        url = f"{GITHUB_SEARCH}?q={quote_plus(q)}&sort=stars&order=desc&per_page=3"
        await _rate_limiter.wait("api.github.com")
        try:
            async with session.get(url, headers=self.gh._headers()) as resp:
                if resp.status == 403:
                    log.warning("GitHub search rate limited; stopping")
                    return {"_rate_limited": True}
                if resp.status != 200:
                    return None
                data = await resp.json()
                items = data.get("items") or []
                if not items:
                    return None
                top = items[0]
                return {
                    "full_name": top.get("full_name"),
                    "stargazers_count": int(top.get("stargazers_count") or 0),
                    "forks_count": int(top.get("forks_count") or 0),
                    "html_url": top.get("html_url"),
                }
        except Exception as e:
            log.warning("GitHub search failed for %s: %s", arxiv_id, e)
            return None

    async def run(self, session: AsyncSession) -> dict:
        run = await start_run(session, self.module, self.source)
        fetched = new = updated = failed = 0

        try:
            papers: Iterable[Paper] = (
                await session.execute(
                    select(Paper)
                    .where(Paper.github_repo.is_(None))
                    .where(Paper.source == "arxiv")
                    .order_by(Paper.published_at.desc().nullslast())
                    .limit(self.max_papers)
                )
            ).scalars().all()

            fetched = len(papers)

            async with http_session() as http:
                for p in papers:
                    if not p.source_id:
                        continue
                    result = await self._search_best_repo(http, p.source_id)
                    if result is None:
                        failed += 1
                        continue
                    if result.get("_rate_limited"):
                        await finish_run(
                            session, run, status="failed",
                            fetched=fetched, new=new, updated=updated, failed=failed,
                            message="GitHub rate limit reached",
                        )
                        await session.commit()
                        return {"fetched": fetched, "new": new, "updated": updated, "failed": failed, "rate_limited": True}
                    p.github_repo = result["full_name"]
                    p.github_stars = result["stargazers_count"]
                    p.github_forks = result["forks_count"]
                    updated += 1

            await session.flush()
            await finish_run(
                session, run, status="success",
                fetched=fetched, new=new, updated=updated, failed=failed,
                message=f"enriched {updated}/{fetched} papers",
            )
            await session.commit()
            log.info("github enrichment: updated=%d/%d failed=%d", updated, fetched, failed)
        except Exception as e:
            log.exception("github enrichment failed")
            await finish_run(session, run, status="failed", fetched=fetched, new=new, updated=updated, failed=failed, message=str(e))
            await session.commit()
            raise

        return {"fetched": fetched, "new": new, "updated": updated, "failed": failed}
