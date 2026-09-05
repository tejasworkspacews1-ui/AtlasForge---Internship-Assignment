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
"""News ingestor — RSS/Atom feeds with 24-hour freshness validation.

Only items published within the last 24h are kept; older items are recorded as
fetched but rejected for failing the freshness check. This guarantees the news
table is always recent (per assignment requirement).

Free, public RSS sources only.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

import feedparser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.http import _rate_limiter, http_session
from app.core.logging import get_logger
from app.models.orm import NewsItem
from app.services.ingestors.base import Ingestor
from app.services.pipeline_log import finish_run, start_run

log = get_logger(__name__)

# Verified free public AI/tech RSS feeds
DEFAULT_FEEDS: list[tuple[str, str]] = [
    ("techcrunch_ai", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("theverge_ai", "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"),
    ("venturebeat_ai", "https://venturebeat.com/category/ai/feed/"),
    ("mit_news_ai", "https://news.mit.edu/topic/mitartificial-intelligence2-rss.xml"),
]

MAX_AGE_HOURS = 24


def _parse_dt(entry) -> datetime | None:
    for key in ("published", "updated", "created"):
        val = entry.get(key)
        if not val:
            continue
        try:
            dt = parsedate_to_datetime(val)
            if dt is None:
                continue
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            continue
    for key in ("published_parsed", "updated_parsed"):
        st = entry.get(key)
        if st:
            try:
                return datetime(*st[:6], tzinfo=timezone.utc)
            except Exception:
                continue
    return None


class NewsIngestor(Ingestor):
    name = "news_rss"
    module = "news"
    source = "RSS Feeds"

    def __init__(self, feeds: list[tuple[str, str]] | None = None, max_age_hours: int = MAX_AGE_HOURS):
        self.feeds = feeds or DEFAULT_FEEDS
        self.max_age_hours = max_age_hours

    async def run(self, session: AsyncSession) -> dict:
        run = await start_run(session, self.module, self.source)
        fetched = new = updated = failed = 0
        stale_skipped = 0
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self.max_age_hours)

        try:
            async with http_session() as http:
                for source_name, url in self.feeds:
                    try:
                        from urllib.parse import urlparse
                        await _rate_limiter.wait(urlparse(url).netloc)
                        async with http.get(url) as resp:
                            resp.raise_for_status()
                            content = await resp.text()
                    except Exception as e:
                        log.warning("news fetch failed for %s: %s", url, e)
                        failed += 1
                        continue

                    parsed = feedparser.parse(content)
                    feed_new = 0
                    feed_stale = 0
                    for entry in parsed.entries:
                        fetched += 1
                        link = (entry.get("link") or "").strip()
                        title = (entry.get("title") or "").strip()
                        if not link or not title:
                            failed += 1
                            continue

                        published = _parse_dt(entry)
                        if published is None or published < cutoff:
                            feed_stale += 1
                            stale_skipped += 1
                            continue

                        summary = entry.get("summary") or entry.get("description")
                        author = entry.get("author")
                        categories = [t.get("term") for t in entry.get("tags", []) if t.get("term")]

                        existing = (
                            await session.execute(
                                select(NewsItem).where(NewsItem.source == source_name, NewsItem.url == link)
                            )
                        ).scalar_one_or_none()

                        if existing is None:
                            session.add(
                                NewsItem(
                                    source=source_name,
                                    title=title,
                                    url=link,
                                    summary=summary,
                                    author=author,
                                    published_at=published,
                                    categories=categories,
                                )
                            )
                            new += 1
                            feed_new += 1
                        else:
                            existing.title = title
                            existing.summary = summary
                            existing.author = author
                            existing.published_at = published
                            existing.categories = categories
                            updated += 1

                    log.info("news[%s]: new=%d stale=%d", source_name, feed_new, feed_stale)

            await session.flush()
            await finish_run(
                session, run,
                status="success",
                fetched=fetched, new=new, updated=updated, failed=failed,
                message=f"feeds={len(self.feeds)} kept={new+updated} stale_skipped={stale_skipped}",
            )
            await session.commit()
            log.info("news ingestor: fetched=%d new=%d updated=%d stale_skipped=%d failed=%d",
                     fetched, new, updated, stale_skipped, failed)
        except Exception as e:
            log.exception("news ingestor failed")
            await finish_run(session, run, status="failed", fetched=fetched, new=new, updated=updated,
                             failed=failed, message=str(e))
            await session.commit()
            raise

        return {"fetched": fetched, "new": new, "updated": updated, "failed": failed,
                "stale_skipped": stale_skipped, "freshness_window_hours": self.max_age_hours}
