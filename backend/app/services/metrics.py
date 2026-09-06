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
"""Dashboard metrics: counts, freshness, health."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import (
    Job,
    NewsItem,
    Paper,
    PipelineRun,
    Product,
    Startup,
)
from app.schemas.api import DashboardMetricsOut, ModuleCounts


async def compute_dashboard(session: AsyncSession) -> DashboardMetricsOut:
    since_24h = datetime.now(timezone.utc) - timedelta(hours=24)

    paper_n = await session.scalar(select(func.count()).select_from(Paper))
    startup_n = await session.scalar(select(func.count()).select_from(Startup))
    product_n = await session.scalar(select(func.count()).select_from(Product))
    news_n = await session.scalar(select(func.count()).select_from(NewsItem))
    job_n = await session.scalar(select(func.count()).select_from(Job))

    by_module = ModuleCounts(
        papers=paper_n or 0,
        startups=startup_n or 0,
        products=product_n or 0,
        news=news_n or 0,
        jobs=job_n or 0,
    )
    total = sum(by_module.model_dump().values())

    fresh_window = datetime.now(timezone.utc) - timedelta(hours=24)
    fresh_news = await session.scalar(
        select(func.count()).select_from(NewsItem).where(NewsItem.published_at >= fresh_window)
    )
    fresh_jobs = await session.scalar(
        select(func.count()).select_from(Job).where(Job.posted_at >= fresh_window)
    )
    fresh_papers = await session.scalar(
        select(func.count()).select_from(Paper).where(Paper.published_at >= fresh_window)
    )

    new_24h = await session.scalar(
        select(func.count()).select_from(Paper).where(Paper.created_at >= since_24h)
    ) + await session.scalar(
        select(func.count()).select_from(Startup).where(Startup.created_at >= since_24h)
    ) + await session.scalar(
        select(func.count()).select_from(Product).where(Product.created_at >= since_24h)
    ) + await session.scalar(
        select(func.count()).select_from(NewsItem).where(NewsItem.created_at >= since_24h)
    ) + await session.scalar(
        select(func.count()).select_from(Job).where(Job.created_at >= since_24h)
    )

    last_10 = (await session.execute(
        select(PipelineRun).order_by(PipelineRun.started_at.desc()).limit(10)
    )).scalars().all()

    if last_10:
        ok = sum(1 for r in last_10 if r.status == "success")
        health = round(100.0 * ok / len(last_10), 1)
    else:
        health = 100.0

    fresh_signals = [bool(fresh_news), bool(fresh_jobs), bool(fresh_papers), total > 0]
    freshness = round(100.0 * sum(1 for s in fresh_signals if s) / len(fresh_signals), 1)

    return DashboardMetricsOut(
        total_records=total,
        records_last_24h=int(new_24h or 0),
        pipeline_health=health,
        freshness_score=freshness,
        by_module=by_module,
    )
