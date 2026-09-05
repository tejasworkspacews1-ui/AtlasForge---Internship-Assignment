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
"""Polite async HTTP client shared by all ingestors."""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator, Iterable

import aiohttp

from .config import settings
from .logging import get_logger

log = get_logger(__name__)


class RateLimiter:
    """Simple token-bucket per-host rate limiter."""

    def __init__(self, per_host_interval: float):
        self._interval = per_host_interval
        self._locks: dict[str, asyncio.Lock] = {}
        self._last: dict[str, float] = {}

    async def wait(self, host: str) -> None:
        lock = self._locks.setdefault(host, asyncio.Lock())
        async with lock:
            now = asyncio.get_event_loop().time()
            last = self._last.get(host, 0.0)
            delay = self._interval - (now - last)
            if delay > 0:
                await asyncio.sleep(delay)
            self._last[host] = asyncio.get_event_loop().time()


_rate_limiter = RateLimiter(settings.rate_limit_per_host)


@asynccontextmanager
async def http_session() -> AsyncIterator[aiohttp.ClientSession]:
    timeout = aiohttp.ClientTimeout(total=settings.request_timeout_seconds)
    headers = {
        "User-Agent": settings.user_agent,
        "Accept": "application/json, text/xml, text/html;q=0.9, */*;q=0.5",
    }
    async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
        yield session


async def get_json(session: aiohttp.ClientSession, url: str, params: dict | None = None) -> dict | list:
    from urllib.parse import urlparse

    host = urlparse(url).netloc
    await _rate_limiter.wait(host)
    async with session.get(url, params=params) as resp:
        resp.raise_for_status()
        return await resp.json()


async def get_text(session: aiohttp.ClientSession, url: str) -> str:
    from urllib.parse import urlparse

    host = urlparse(url).netloc
    await _rate_limiter.wait(host)
    async with session.get(url) as resp:
        resp.raise_for_status()
        return await resp.text()


async def gather_limited(tasks: Iterable, limit: int = 5):
    sem = asyncio.Semaphore(limit)

    async def _wrap(coro):
        async with sem:
            return await coro

    return await asyncio.gather(*(_wrap(c) for c in tasks), return_exceptions=True)
