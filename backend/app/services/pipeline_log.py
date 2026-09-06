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
"""Pipeline audit log helpers."""
from __future__ import annotations

import secrets
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.orm import PipelineRun

log = get_logger(__name__)


def _new_run_id() -> str:
    return f"run_{secrets.token_hex(6)}"


async def start_run(session: AsyncSession, module: str, source: str) -> PipelineRun:
    run = PipelineRun(
        run_id=_new_run_id(),
        module=module,
        source=source,
        status="running",
        started_at=datetime.now(timezone.utc),
    )
    session.add(run)
    await session.flush()
    log.info("Pipeline started: %s [%s/%s]", run.run_id, module, source)
    return run


async def finish_run(
    session: AsyncSession,
    run: PipelineRun,
    *,
    status: str,
    fetched: int = 0,
    new: int = 0,
    updated: int = 0,
    failed: int = 0,
    message: str | None = None,
) -> None:
    run.status = status
    run.finished_at = datetime.now(timezone.utc)
    run.records_fetched = fetched
    run.records_new = new
    run.records_updated = updated
    run.records_failed = failed
    run.message = message
    log.info(
        "Pipeline finished: %s status=%s fetched=%d new=%d updated=%d failed=%d",
        run.run_id, status, fetched, new, updated, failed,
    )
