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
"""Ingestor registry — Phase B exposes the interface, Phase C+ provides real ones."""
from __future__ import annotations

from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession


class Ingestor(Protocol):
    name: str
    module: str
    source: str

    async def run(self, session: AsyncSession) -> dict:
        return {"fetched": 0, "new": 0, "updated": 0, "failed": 0}


REGISTRY: dict[str, Ingestor] = {}


def register(ingestor: Ingestor) -> Ingestor:
    REGISTRY[f"{ingestor.module}:{ingestor.name}"] = ingestor
    return ingestor
