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
"""Generic paginated search for any ORM model."""
from __future__ import annotations

from typing import TypeVar

from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import Paper, Job, NewsItem, Product, Startup

M = TypeVar("M")

MODEL_BY_KEY: dict[str, type] = {
    "papers": Paper,
    "startups": Startup,
    "products": Product,
    "news": NewsItem,
    "jobs": Job,
}

SEARCHABLE: dict[str, list[str]] = {
    "papers": ["title", "abstract"],
    "startups": ["name", "description", "focus_area", "location"],
    "products": ["name", "company", "category", "description"],
    "news": ["title", "summary", "author"],
    "jobs": ["title", "company", "location", "description"],
}


async def paginate(
    session: AsyncSession,
    module: str,
    *,
    page: int = 1,
    page_size: int = 25,
    q: str | None = None,
    sort: str | None = None,
    order: str = "desc",
) -> tuple[list, int]:
    model = MODEL_BY_KEY[module]
    page = max(1, page)
    page_size = max(1, min(page_size, 100))

    stmt = select(model)
    count_stmt = select(func.count()).select_from(model)

    if q:
        from sqlalchemy import cast, String

        like = f"%{q.lower()}%"
        cols = SEARCHABLE[module]
        conds = [func.lower(cast(getattr(model, c), String)).like(like) for c in cols]
        from sqlalchemy import or_

        stmt = stmt.where(or_(*conds))
        count_stmt = count_stmt.where(or_(*conds))

    if sort and hasattr(model, sort):
        col = getattr(model, sort)
        stmt = stmt.order_by(desc(col) if order == "desc" else asc(col))

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    items = (await session.execute(stmt)).scalars().unique().all()
    total = await session.scalar(count_stmt) or 0
    return list(items), int(total)
