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
"""Health + dashboard endpoints."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

from app.api.deps import DbDep
from app.schemas.api import DashboardMetricsOut
from app.services.metrics import compute_dashboard

router = APIRouter(prefix="/api", tags=["core"])


@router.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "service": "atlasforge",
        "version": "0.1.0",
        "time": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/dashboard", response_model=DashboardMetricsOut)
async def dashboard(session: DbDep) -> DashboardMetricsOut:
    return await compute_dashboard(session)
