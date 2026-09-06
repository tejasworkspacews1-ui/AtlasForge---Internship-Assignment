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
"""Ingestor dispatcher — used by API endpoint and CLI."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ingestors.arxiv import ArxivIngestor
from app.services.ingestors.github_enrichment import GitHubEnrichmentIngestor
from app.services.ingestors.news import NewsIngestor
from app.services.ingestors.jobs import JobsIngestor
from app.services.ingestors.llm_enrich import LLMEnrichmentIngestor
from app.services.ingestors.entity_resolution import EntityResolutionIngestor

AVAILABLE = {
    "arxiv": ("papers", "arXiv API", lambda: ArxivIngestor(max_results=30)),
    "github": ("papers", "GitHub API", lambda: GitHubEnrichmentIngestor(max_papers=15)),
    "news": ("news", "RSS Feeds", lambda: NewsIngestor()),
    "jobs": ("jobs", "RemoteOK + Arbeitnow", lambda: JobsIngestor()),
    "llm_enrich": ("news", "Multi-tier LLM", lambda: LLMEnrichmentIngestor(max_items=25)),
    "entity_resolution": ("entities", "Seed dict + fuzzy + DB", lambda: EntityResolutionIngestor()),
}


async def run_ingestor(session: AsyncSession, key: str) -> dict:
    if key not in AVAILABLE:
        raise ValueError(f"Unknown ingestor '{key}'. Available: {list(AVAILABLE)}")
    module, source, factory = AVAILABLE[key]
    ingestor = factory()
    return await ingestor.run(session)
