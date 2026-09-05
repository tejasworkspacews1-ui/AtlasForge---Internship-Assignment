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
"""CLI: run any ingestor from the command line.

Usage:
    python -m scripts.run_ingestor arxiv
    python -m scripts.run_ingestor github
"""
from __future__ import annotations

import asyncio
import sys

from app.db.session import init_db, session_scope
from app.services.ingestors.dispatcher import AVAILABLE, run_ingestor


async def main(name: str) -> int:
    if name not in AVAILABLE:
        print(f"Unknown ingestor '{name}'. Available: {list(AVAILABLE)}")
        return 1
    await init_db()
    async with session_scope() as session:
        result = await run_ingestor(session, name)
        print(f"Result: {result}")
    return 0


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "arxiv"
    raise SystemExit(asyncio.run(main(target)))
