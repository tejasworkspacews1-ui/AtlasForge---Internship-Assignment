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
"""LLM status endpoint — honestly reports which tiers are configured."""
from __future__ import annotations

import os

from fastapi import APIRouter

from app.services.llm.providers import build_providers

router = APIRouter(prefix="/api/llm", tags=["llm"])


@router.get("/status")
async def status() -> dict:
    providers = build_providers()
    return {
        "configured": [
            {"name": p.name, "model": getattr(p, "model", "?")} for p in providers
        ],
        "available_env_keys": [k for k in ("GEMINI_API_KEY", "GROQ_API_KEY", "DEEPSEEK_API_KEY") if os.getenv(k)],
        "tier_order": ["gemini", "groq", "deepseek"],
        "fallback": "deterministic (rule-based)",
    }
