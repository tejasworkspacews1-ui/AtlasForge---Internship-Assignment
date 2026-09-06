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
"""Pipeline audit endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Query

from sqlalchemy import desc, select

from app.api.deps import DbDep
from app.models.orm import PipelineRun
from app.schemas.api import PageResult, PipelineRunOut

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


@router.get("/runs", response_model=PageResult[PipelineRunOut])
async def list_runs(
    session: DbDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    module: str | None = Query(None),
):
    stmt = select(PipelineRun).order_by(desc(PipelineRun.started_at))
    count_stmt = select(PipelineRun.run_id)
    if module:
        stmt = stmt.where(PipelineRun.module == module)
        count_stmt = count_stmt.where(PipelineRun.module == module)
    total = len((await session.execute(count_stmt)).scalars().all())
    runs = (
        await session.execute(stmt.offset((page - 1) * page_size).limit(page_size))
    ).scalars().all()
    return PageResult(
        items=[PipelineRunOut.model_validate(r) for r in runs],
        total=total,
        page=page,
        page_size=page_size,
    )
