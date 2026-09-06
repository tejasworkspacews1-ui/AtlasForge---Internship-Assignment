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
"""Centralized settings loaded from environment with sane local defaults."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = BACKEND_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)


@dataclass(frozen=True)
class Settings:
    app_name: str = "AtlasForge"
    api_host: str = os.getenv("ATLAS_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("ATLAS_PORT", "8000"))
    database_url: str = os.getenv("ATLAS_DB_URL", f"sqlite+aiosqlite:///{DATA_DIR}/atlas.db")
    cors_origins: tuple[str, ...] = tuple(
        o.strip()
        for o in os.getenv(
            "ATLAS_CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,https://atlasforgesmartresources.vercel.app,https://atlasforge-smartresources.onrender.com",
        ).split(",")
        if o.strip()
    )
    log_level: str = os.getenv("ATLAS_LOG_LEVEL", "INFO")
    user_agent: str = os.getenv(
        "ATLAS_UA",
        "AtlasForge/0.1 (+https://github.com/local/atlasforge) Python-aiohttp",
    )
    rate_limit_per_host: float = float(os.getenv("ATLAS_RATE_LIMIT", "2.0"))
    request_timeout_seconds: float = float(os.getenv("ATLAS_TIMEOUT", "20.0"))


settings = Settings()
