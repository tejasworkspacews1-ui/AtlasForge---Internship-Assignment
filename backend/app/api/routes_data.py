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
"""Data module endpoints: search/paginate papers, startups, etc."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.api.deps import DbDep
from app.models.orm import Job, NewsItem, Paper, Product, Startup
from app.schemas.api import (
    JobOut,
    NewsOut,
    PageResult,
    PaperOut,
    ProductOut,
    StartupOut,
)
from app.services.search import paginate

router = APIRouter(prefix="/api", tags=["data"])

MODULES = {
    "papers": (Paper, PaperOut),
    "startups": (Startup, StartupOut),
    "products": (Product, ProductOut),
    "news": (NewsItem, NewsOut),
    "jobs": (Job, JobOut),
}


@router.get("/{module}", response_model=PageResult)
async def list_module(
    module: str,
    session: DbDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    q: str | None = Query(None),
    sort: str | None = Query(None),
    order: str = Query("desc", pattern="^(asc|desc)$"),
):
    if module not in MODULES:
        raise HTTPException(404, f"Unknown module '{module}'")
    items, total = await paginate(
        session, module, page=page, page_size=page_size, q=q, sort=sort, order=order
    )
    schema = MODULES[module][1]
    return PageResult(
        items=[schema.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
    )
