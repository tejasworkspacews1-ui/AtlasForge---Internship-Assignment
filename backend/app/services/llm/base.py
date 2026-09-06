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
"""LLM provider abstraction with retry/backoff and chunking.

Each provider implements a common interface. The MultiTierAdapter tries
providers in order, falling back on 429/5xx. 413 (payload too large) is
handled at the chunking layer BEFORE the request goes out.
"""
from __future__ import annotations

import asyncio
import json
import os
import random
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class LLMResponse:
    text: str
    provider: str
    model: str
    usage: dict[str, int]


class ProviderError(Exception):
    def __init__(self, provider: str, status: int | None, message: str, retryable: bool = False):
        super().__init__(f"{provider} [{status}]: {message}")
        self.provider = provider
        self.status = status
        self.retryable = retryable


class LLMProvider(Protocol):
    name: str
    model: str

    async def complete(self, prompt: str, *, max_tokens: int = 512, temperature: float = 0.0) -> LLMResponse: ...


async def with_retries(fn, *, attempts: int = 4, base_delay: float = 0.8, max_delay: float = 16.0):
    """Exponential backoff with jitter for retryable errors (429/5xx)."""
    last_err: Exception | None = None
    for i in range(attempts):
        try:
            return await fn()
        except ProviderError as e:
            last_err = e
            if not e.retryable or i == attempts - 1:
                raise
            delay = min(max_delay, base_delay * (2 ** i))
            delay += random.uniform(0, delay * 0.25)
            await asyncio.sleep(delay)
    if last_err:
        raise last_err
    raise RuntimeError("with_retries: exhausted without error")


def chunk_text(text: str, max_chars: int = 12000, overlap: int = 200) -> list[str]:
    """Split text into chunks safe for ~16k-token context models with overlap."""
    text = (text or "").strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        chunk = text[start:end]
        chunks.append(chunk)
        if end >= len(text):
            break
        start = end - overlap
    return chunks


def merge_json_chunks(chunks: list[str]) -> dict | list | None:
    """Best-effort merge of JSON arrays returned per chunk."""
    parsed = []
    for c in chunks:
        s = (c or "").strip()
        if not s:
            continue
        if s.startswith("```"):
            s = s.strip("`")
            if s.startswith("json"):
                s = s[4:]
            s = s.strip()
        try:
            obj = json.loads(s)
        except Exception:
            continue
        if isinstance(obj, list):
            parsed.extend(obj)
        elif isinstance(obj, dict):
            parsed.append(obj)
    return parsed or None


def safe_json_parse(text: str) -> dict | list | None:
    s = (text or "").strip()
    if not s:
        return None
    if s.startswith("```"):
        s = s.strip("`")
        if s.startswith("json"):
            s = s[4:]
        s = s.strip()
    try:
        return json.loads(s)
    except Exception:
        start = s.find("{")
        end = s.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(s[start:end + 1])
            except Exception:
                return None
        return None


@dataclass
class TierConfig:
    name: str
    model: str
    api_key_env: str | None
    base_url: str


TIER_ORDER: list[TierConfig] = [
    TierConfig("gemini", "gemini-1.5-flash", "GEMINI_API_KEY", "https://generativelanguage.googleapis.com/v1beta"),
    TierConfig("groq", "llama-3.1-8b-instant", "GROQ_API_KEY", "https://api.groq.com/openai/v1"),
    TierConfig("deepseek", "deepseek-chat", "DEEPSEEK_API_KEY", "https://api.deepseek.com/v1"),
]
