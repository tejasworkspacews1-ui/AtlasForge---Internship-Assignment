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
"""Export endpoints — CSV / TSV download per module."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import DbDep
from app.models.orm import Entity, EntityAlias, Job, NewsItem, Paper, Product, Startup
from app.services.export import MODULE_COLUMNS, to_csv, to_tsv

router = APIRouter(prefix="/api/export", tags=["export"])

MODEL_BY_MODULE = {
    "papers": Paper,
    "startups": Startup,
    "products": Product,
    "news": NewsItem,
    "jobs": Job,
}


def _filename(module: str, ext: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"atlasforge_{module}_{ts}.{ext}"


@router.get("/available")
async def available() -> dict:
    return {
        "modules": list(MODULE_COLUMNS.keys()),
        "formats": ["csv", "tsv"],
        "column_counts": {k: len(v) for k, v in MODULE_COLUMNS.items()},
    }


async def _load_entities(session, limit: int):
    rows = (
        await session.execute(
            select(Entity)
            .options(selectinload(Entity.aliases))
            .order_by(Entity.canonical.asc())
            .limit(limit)
        )
    ).scalars().all()
    return rows


async def _load_module(session, module: str, limit: int):
    if module == "entities":
        return await _load_entities(session, limit)
    model = MODEL_BY_MODULE[module]
    rows = (
        await session.execute(select(model).order_by(model.id.asc()).limit(limit))
    ).scalars().unique().all()
    return rows


@router.get("/{module}.csv")
async def export_csv(
    module: str,
    session: DbDep,
    limit: int = Query(10000, ge=1, le=100000),
) -> Response:
    if module not in MODULE_COLUMNS:
        raise HTTPException(404, f"Unknown module '{module}'")
    rows = await _load_module(session, module, limit)
    content = to_csv(module, rows)
    return Response(
        content=content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{_filename(module, "csv")}"',
            "X-AtlasForge-Rows": str(len(rows)),
        },
    )


@router.get("/{module}.tsv")
async def export_tsv(
    module: str,
    session: DbDep,
    limit: int = Query(10000, ge=1, le=100000),
) -> Response:
    if module not in MODULE_COLUMNS:
        raise HTTPException(404, f"Unknown module '{module}'")
    rows = await _load_module(session, module, limit)
    content = to_tsv(module, rows)
    return Response(
        content=content,
        media_type="text/tab-separated-values",
        headers={
            "Content-Disposition": f'attachment; filename="{_filename(module, "tsv")}"',
            "X-AtlasForge-Rows": str(len(rows)),
        },
    )
