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
"""Entity resolution endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Query
from sqlalchemy import desc, func, select

from app.api.deps import DbDep
from app.models.orm import Entity, EntityAlias
from app.schemas.api import PageResult

router = APIRouter(prefix="/api/entities", tags=["entities"])


@router.get("/clusters")
async def list_clusters(
    session: DbDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    q: str | None = Query(None),
):
    stmt = (
        select(
            Entity.id,
            Entity.canonical,
            Entity.kind,
            Entity.confidence,
            func.count(EntityAlias.id).label("alias_count"),
        )
        .join(EntityAlias, EntityAlias.entity_id == Entity.id, isouter=True)
        .group_by(Entity.id, Entity.canonical, Entity.kind, Entity.confidence)
        .order_by(desc("alias_count"), Entity.canonical.asc())
    )
    count_stmt = select(func.count()).select_from(Entity)
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(func.lower(Entity.canonical).like(like))
        count_stmt = count_stmt.where(func.lower(Entity.canonical).like(like))

    total = await session.scalar(count_stmt) or 0
    rows = (
        await session.execute(stmt.offset((page - 1) * page_size).limit(page_size))
    ).all()

    items = []
    for r in rows:
        ent_id = r.id
        aliases = (
            await session.execute(
                select(EntityAlias).where(EntityAlias.entity_id == ent_id)
            )
        ).scalars().all()
        items.append({
            "id": ent_id,
            "canonical": r.canonical,
            "kind": r.kind,
            "confidence": float(r.confidence),
            "alias_count": int(r.alias_count),
            "aliases": [
                {
                    "alias": a.alias,
                    "confidence": float(a.confidence),
                    "reasoning": a.reasoning,
                }
                for a in aliases
            ],
        })

    return PageResult(items=items, total=int(total), page=page, page_size=page_size)


@router.post("/resolve")
async def resolve_endpoint(payload: dict, session: DbDep) -> dict:
    from app.services.entity_resolver import resolve

    name = (payload or {}).get("name", "")
    kind = (payload or {}).get("kind", "company")
    if not name:
        return {"error": "name is required"}
    result = await resolve(name, kind=kind, db_session=session)
    return {
        "input": name,
        "canonical": result.canonical,
        "confidence": result.confidence,
        "reasoning": result.reasoning,
        "method": result.method,
        "is_new": result.is_new,
    }
