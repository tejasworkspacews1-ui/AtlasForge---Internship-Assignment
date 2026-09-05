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
"""Manual ingestor trigger endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.api.deps import DbDep
from app.services.ingestors.dispatcher import AVAILABLE, run_ingestor

router = APIRouter(prefix="/api/ingest", tags=["ingest"])


@router.get("/available")
async def available() -> dict:
    return {
        key: {"module": mod, "source": src}
        for key, (mod, src, _) in AVAILABLE.items()
    }


@router.post("/{key}")
async def trigger(key: str, session: DbDep) -> dict:
    try:
        result = await run_ingestor(session, key)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return result
