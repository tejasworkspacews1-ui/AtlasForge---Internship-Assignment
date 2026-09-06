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
"""arXiv ingestor — public arXiv API (no key required, free).

Pulls recent papers from AI-relevant arXiv categories, deduplicates, and stores.
Docs: https://arxiv.org/help/api
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.http import http_session
from app.core.logging import get_logger
from app.models.orm import Paper
from app.services.ingestors.base import Ingestor
from app.services.pipeline_log import finish_run, start_run

log = get_logger(__name__)

ARXIV_API = "http://export.arxiv.org/api/query"
NS = {"a": "http://www.w3.org/2005/Atom"}

AI_CATEGORIES = [
    "cs.AI",  # Artificial Intelligence
    "cs.LG",  # Machine Learning
    "cs.CL",  # Computation & Language
    "cs.CV",  # Computer Vision
    "cs.RO",  # Robotics
    "cs.IR",  # Information Retrieval
    "stat.ML",
]


def _parse_entry(entry: ET.Element) -> dict[str, Any]:
    eid = entry.find("a:id", NS)
    title = entry.find("a:title", NS)
    summary = entry.find("a:summary", NS)
    published = entry.find("a:published", NS)
    updated = entry.find("a:updated", NS)

    authors = [a.findtext("a:name", default="", namespaces=NS) for a in entry.findall("a:author", NS)]
    authors = [a for a in authors if a]

    cats = [c.attrib.get("term", "") for c in entry.findall("a:category", NS)]

    pdf_url = None
    for link in entry.findall("a:link", NS):
        if link.attrib.get("title") == "pdf":
            pdf_url = link.attrib.get("href")
            break

    source_id = (eid.text or "").rsplit("/", 1)[-1] if eid is not None and eid.text else ""
    return {
        "source": "arxiv",
        "source_id": source_id,
        "title": (title.text or "").strip().replace("\n", " ") if title is not None else "",
        "abstract": (summary.text or "").strip() if summary is not None else None,
        "authors_json": authors,
        "categories": cats,
        "url": eid.text.strip() if eid is not None and eid.text else "",
        "pdf_url": pdf_url,
        "published_at": _parse_dt(published.text) if published is not None else None,
        "_updated": _parse_dt(updated.text) if updated is not None else None,
    }


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


class ArxivIngestor(Ingestor):
    name = "arxiv"
    module = "papers"
    source = "arXiv API"

    def __init__(self, max_results: int = 30, categories: list[str] | None = None):
        self.max_results = max_results
        self.categories = categories or AI_CATEGORIES

    async def run(self, session: AsyncSession) -> dict:
        run = await start_run(session, self.module, self.source)
        fetched = new = updated = failed = 0

        try:
            cat_query = " OR ".join(f"cat:{c}" for c in self.categories)
            params = {
                "search_query": f"({cat_query})",
                "start": "0",
                "max_results": str(self.max_results),
                "sortBy": "submittedDate",
                "sortOrder": "descending",
            }

            async with http_session() as http:
                from app.core.http import _rate_limiter
                from urllib.parse import urlparse
                await _rate_limiter.wait(urlparse(ARXIV_API).netloc)
                import aiohttp
                async with http.get(ARXIV_API, params=params) as resp:
                    resp.raise_for_status()
                    xml_text = await resp.text()

            root = ET.fromstring(xml_text)
            entries = root.findall("a:entry", NS)
            fetched = len(entries)

            for raw in entries:
                try:
                    data = _parse_entry(raw)
                    if not data["source_id"] or not data["title"]:
                        failed += 1
                        continue

                    existing = (
                        await session.execute(
                            select(Paper).where(Paper.source == "arxiv", Paper.source_id == data["source_id"])
                        )
                    ).scalar_one_or_none()

                    if existing is None:
                        session.add(Paper(**{k: v for k, v in data.items() if not k.startswith("_")}))
                        new += 1
                    else:
                        for k, v in data.items():
                            if not k.startswith("_") and v is not None:
                                setattr(existing, k, v)
                        updated += 1
                except Exception as e:
                    log.warning("arxiv parse failed: %s", e)
                    failed += 1

            await session.flush()
            await finish_run(
                session, run, status="success",
                fetched=fetched, new=new, updated=updated, failed=failed,
                message=f"categories={','.join(self.categories)}",
            )
            await session.commit()
            log.info("arxiv ingestor: fetched=%d new=%d updated=%d failed=%d", fetched, new, updated, failed)
        except Exception as e:
            log.exception("arxiv ingestor failed")
            await finish_run(session, run, status="failed", fetched=fetched, new=new, updated=updated, failed=failed, message=str(e))
            await session.commit()
            raise

        return {"fetched": fetched, "new": new, "updated": updated, "failed": failed}
