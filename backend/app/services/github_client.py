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
"""GitHub REST API client.

Free tier: 60 req/hour unauthenticated, 5000/hour with token.
We use unauthenticated by default. If GITHUB_TOKEN is set, we use it for higher rate limit.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

import aiohttp

from app.core.http import _rate_limiter
from app.core.logging import get_logger
from urllib.parse import urlparse

log = get_logger(__name__)

GITHUB_API = "https://api.github.com"


@dataclass
class RepoStats:
    full_name: str
    stars: int
    forks: int
    description: str | None
    html_url: str
    exists: bool


class GitHubClient:
    def __init__(self, token: str | None = None):
        self.token = token or os.getenv("GITHUB_TOKEN")

    def _headers(self) -> dict:
        h = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    async def get_repo(self, session: aiohttp.ClientSession, repo: str) -> RepoStats | None:
        """repo like 'owner/name'. Returns None on 404, RepoStats otherwise."""
        host = urlparse(GITHUB_API).netloc
        await _rate_limiter.wait(host)
        url = f"{GITHUB_API}/repos/{repo}"
        try:
            async with session.get(url, headers=self._headers()) as resp:
                if resp.status == 404:
                    return RepoStats(full_name=repo, stars=0, forks=0, description=None, html_url=f"https://github.com/{repo}", exists=False)
                if resp.status == 403:
                    log.warning("GitHub rate limit hit for %s", repo)
                    return None
                resp.raise_for_status()
                data = await resp.json()
                return RepoStats(
                    full_name=data.get("full_name", repo),
                    stars=int(data.get("stargazers_count") or 0),
                    forks=int(data.get("forks_count") or 0),
                    description=data.get("description"),
                    html_url=data.get("html_url", f"https://github.com/{repo}"),
                    exists=True,
                )
        except Exception as e:
            log.warning("GitHub fetch failed for %s: %s", repo, e)
            return None
