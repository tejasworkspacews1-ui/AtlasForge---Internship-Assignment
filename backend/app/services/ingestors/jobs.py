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
"""Jobs ingestor — public JSON APIs with 24-hour freshness check.

Sources (free, no key, public):
  - RemoteOK: https://remoteok.com/api (JSON list, AI filter via tags)
  - Arbeitnow: https://www.arbeitnow.com/api/job-board-api (free public)

Only items posted within the last 24h are stored. Older ones are counted as
fetched but rejected (logged via stale_skipped counter).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import feedparser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.http import _rate_limiter, get_json, http_session
from app.core.logging import get_logger
from app.models.orm import Job
from app.services.ingestors.base import Ingestor
from app.services.pipeline_log import finish_run, start_run

log = get_logger(__name__)

REMOTEOK_URL = "https://remoteok.com/api"
ARBEITNOW_URL = "https://www.arbeitnow.com/api/job-board-api"

AI_TITLE_KEYWORDS = (
    " ai ", " ai/", "ai engineer", "ai/ml", "ai ops", "aiops",
    "ml engineer", "machine learning", "deep learning",
    "llm", "gpt", "rag", "nlp", "computer vision",
    "data scientist", "mlops", "ml platform",
    "agent", "agents", "agentic",
    "research engineer", "applied scientist", "model engineer",
    "prompt", "fine-tun", "embedding",
    "neural", "transformer",
)


def _is_ai_job(*texts: str | None) -> bool:
    blob = " ".join((t or "") for t in texts).lower()
    return any(kw in blob for kw in AI_TITLE_KEYWORDS)


def _parse_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


class JobsIngestor(Ingestor):
    name = "jobs_aggregator"
    module = "jobs"
    source = "RemoteOK + Arbeitnow"

    def __init__(self, max_age_hours: int = 72, ai_only: bool = True, max_per_source: int = 40):
        self.max_age_hours = max_age_hours
        self.ai_only = ai_only
        self.max_per_source = max_per_source

    async def _ingest_remoteok(self, session: AsyncSession, cutoff: datetime) -> tuple[int, int, int, int]:
        fetched = new = updated = failed = 0
        try:
            async with http_session() as http:
                await _rate_limiter.wait(urlparse(REMOTEOK_URL).netloc)
                async with http.get(REMOTEOK_URL, headers={"User-Agent": "AtlasForge/0.1"}) as resp:
                    resp.raise_for_status()
                    data = await resp.json(content_type=None)
        except Exception as e:
            log.warning("remoteok fetch failed: %s", e)
            return 0, 0, 0, 1

        if not isinstance(data, list):
            return 0, 0, 0, 0

        for item in data[1:self.max_per_source + 1]:
            fetched += 1
            slug = item.get("slug") or f"rk_{item.get('id')}"
            url = item.get("url") or f"https://remoteok.com/remote-jobs/{slug}"
            title = (item.get("position") or "").strip()
            company = (item.get("company") or "").strip()
            description = item.get("description") or ""
            tags = item.get("tags") or []
            posted_at = _parse_dt(item.get("date"))
            location = (item.get("location") or "").strip() or "Remote"

            if not title or not slug:
                failed += 1
                continue

            if self.ai_only and not _is_ai_job(title):
                continue

            if posted_at is None or posted_at < cutoff:
                continue

            existing = (
                await session.execute(
                    select(Job).where(Job.source == "remoteok", Job.source_id == str(item.get("id") or slug))
                )
            ).scalar_one_or_none()

            row_data = dict(
                source="remoteok",
                source_id=str(item.get("id") or slug),
                title=title,
                company=company or None,
                location=location,
                remote=True,
                url=url,
                description=description[:5000],
                posted_at=posted_at,
                salary_min=float(item["salary_min"]) if item.get("salary_min") else None,
                salary_max=float(item["salary_max"]) if item.get("salary_max") else None,
            )

            if existing is None:
                session.add(Job(**row_data))
                new += 1
            else:
                for k, v in row_data.items():
                    if k == "source_id":
                        continue
                    setattr(existing, k, v)
                updated += 1

        return fetched, new, updated, failed

    async def _ingest_arbeitnow(self, session: AsyncSession, cutoff: datetime) -> tuple[int, int, int, int]:
        fetched = new = updated = failed = 0
        try:
            async with http_session() as http:
                await _rate_limiter.wait(urlparse(ARBEITNOW_URL).netloc)
                async with http.get(ARBEITNOW_URL) as resp:
                    resp.raise_for_status()
                    payload = await resp.json(content_type=None)
        except Exception as e:
            log.warning("arbeitnow fetch failed: %s", e)
            return 0, 0, 0, 1

        jobs = payload.get("data", []) if isinstance(payload, dict) else payload
        for item in jobs[:self.max_per_source]:
            fetched += 1
            slug = item.get("slug") or ""
            url = item.get("url") or f"https://www.arbeitnow.com/jobs/{slug}"
            title = (item.get("title") or "").strip()
            company = (item.get("company_name") or "").strip()
            description = item.get("description") or ""
            tags = item.get("tags") or []
            posted_at = _parse_dt(item.get("created_at"))
            location = (item.get("location") or "").strip() or "Remote"

            if not title or not slug:
                failed += 1
                continue

            if self.ai_only and not _is_ai_job(title):
                continue

            if posted_at is None or posted_at < cutoff:
                continue

            existing = (
                await session.execute(
                    select(Job).where(Job.source == "arbeitnow", Job.source_id == slug)
                )
            ).scalar_one_or_none()

            row_data = dict(
                source="arbeitnow",
                source_id=slug,
                title=title,
                company=company or None,
                location=location,
                remote="remote" in location.lower() or not location,
                url=url,
                description=description[:5000],
                posted_at=posted_at,
                salary_min=None,
                salary_max=None,
            )

            if existing is None:
                session.add(Job(**row_data))
                new += 1
            else:
                for k, v in row_data.items():
                    if k == "source_id":
                        continue
                    setattr(existing, k, v)
                updated += 1

        return fetched, new, updated, failed

    async def run(self, session: AsyncSession) -> dict:
        run = await start_run(session, self.module, self.source)
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self.max_age_hours)

        try:
            rk_f, rk_n, rk_u, rk_fail = await self._ingest_remoteok(session, cutoff)
            an_f, an_n, an_u, an_fail = await self._ingest_arbeitnow(session, cutoff)

            fetched = rk_f + an_f
            new = rk_n + an_n
            updated = rk_u + an_u
            failed = rk_fail + an_fail

            await session.flush()
            await finish_run(
                session, run,
                status="success",
                fetched=fetched, new=new, updated=updated, failed=failed,
                message=f"window={self.max_age_hours}h ai_only={self.ai_only} "
                        f"remoteok[+{rk_n}/~{rk_f}] arbeitnow[+{an_n}/~{an_f}]",
            )
            await session.commit()
            log.info("jobs ingestor: fetched=%d new=%d updated=%d failed=%d", fetched, new, updated, failed)
        except Exception as e:
            log.exception("jobs ingestor failed")
            await finish_run(session, run, status="failed", fetched=fetched, new=new, updated=updated,
                             failed=failed, message=str(e))
            await session.commit()
            raise

        return {
            "fetched": fetched, "new": new, "updated": updated, "failed": failed,
            "freshness_window_hours": self.max_age_hours,
        }
