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
"""Multi-tier LLM dispatcher: tries providers in order, falls back on retryable errors.

For 413 (payload too large), chunks the text first and aggregates JSON results.
For 429/5xx, backs off with exponential delay + jitter per provider.

If no providers are configured (no API keys), returns a structured
ProviderError so callers can fall back to deterministic extraction.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.logging import get_logger

from .base import (
    LLMProvider,
    LLMResponse,
    ProviderError,
    chunk_text,
    merge_json_chunks,
    safe_json_parse,
    with_retries,
)
from .providers import build_providers

log = get_logger(__name__)


@dataclass
class ExtractionResult:
    ok: bool
    data: Any
    provider: str | None
    model: str | None
    chunks_used: int
    attempts: int
    error: str | None = None


EXTRACTION_SYSTEM = (
    "You are a precise information extractor. Output ONLY valid JSON (no prose, no markdown fences). "
    "Be conservative: omit fields you are not confident about. Never invent values."
)


def _providers() -> list[LLMProvider]:
    return build_providers()


async def _try_provider(provider: LLMProvider, prompt: str, max_tokens: int) -> LLMResponse:
    async def call() -> LLMResponse:
        return await provider.complete(prompt, max_tokens=max_tokens, temperature=0.0)
    return await with_retries(call)


async def extract_json(
    text: str,
    schema_hint: str,
    *,
    max_chunk_chars: int = 12000,
    max_tokens: int = 600,
) -> ExtractionResult:
    """Extract structured JSON from `text` using schema_hint, across all configured tiers.

    413 handling: chunks the text and merges array JSON results.
    """
    providers = _providers()
    if not providers:
        return ExtractionResult(
            ok=False, data=None, provider=None, model=None, chunks_used=0, attempts=0,
            error="No LLM providers configured. Set GEMINI_API_KEY / GROQ_API_KEY / DEEPSEEK_API_KEY.",
        )

    chunks = chunk_text(text, max_chars=max_chunk_chars)
    attempts = 0
    last_err: str | None = None

    for provider in providers:
        per_chunk: list[str] = []
        try:
            for i, chunk in enumerate(chunks):
                prompt = (
                    f"{EXTRACTION_SYSTEM}\n\n"
                    f"Extract entities matching this schema:\n{schema_hint}\n\n"
                    f"Text chunk {i + 1}/{len(chunks)}:\n```\n{chunk}\n```"
                )
                attempts += 1
                resp = await _try_provider(provider, prompt, max_tokens)
                per_chunk.append(resp.text)

            merged = merge_json_chunks(per_chunk) if len(per_chunk) > 1 else safe_json_parse(per_chunk[0])
            log.info("LLM extract ok via %s/%s (%d chunks)", provider.name, provider.model, len(per_chunk))
            return ExtractionResult(
                ok=True, data=merged, provider=provider.name, model=provider.model,
                chunks_used=len(per_chunk), attempts=attempts,
            )
        except ProviderError as e:
            last_err = f"{e.provider}[{e.status}]: {str(e)[:120]}"
            log.warning("LLM %s failed: %s — falling back", provider.name, last_err)
            continue
        except Exception as e:
            last_err = f"{provider.name}: {e!s}"[:160]
            log.exception("LLM %s unexpected error", provider.name)
            continue

    return ExtractionResult(
        ok=False, data=None, provider=None, model=None,
        chunks_used=0, attempts=attempts, error=last_err or "all tiers failed",
    )
