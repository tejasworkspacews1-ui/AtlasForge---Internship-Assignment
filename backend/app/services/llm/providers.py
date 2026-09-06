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
"""Provider implementations: Gemini (REST), Groq (OpenAI-compatible), DeepSeek (OpenAI-compatible).

Each provider is only constructed if its API key is present. Missing key
means the tier is skipped (no fabricated calls).
"""
from __future__ import annotations

import os

import aiohttp

from .base import LLMProvider, LLMResponse, ProviderError


class GeminiProvider:
    name = "gemini"
    model = "gemini-1.5-flash"

    def __init__(self, api_key: str, model: str | None = None):
        self.api_key = api_key
        if model:
            self.model = model

    async def complete(self, prompt: str, *, max_tokens: int = 512, temperature: float = 0.0) -> LLMResponse:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        params = {"key": self.api_key}
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": max_tokens, "temperature": temperature},
        }
        async with aiohttp.ClientSession() as s:
            async with s.post(url, params=params, json=body, timeout=aiohttp.ClientTimeout(total=30)) as r:
                if r.status in (429, 500, 502, 503, 504):
                    raise ProviderError(self.name, r.status, await r.text(), retryable=True)
                if r.status == 413:
                    raise ProviderError(self.name, r.status, "payload too large", retryable=False)
                if r.status != 200:
                    raise ProviderError(self.name, r.status, await r.text(), retryable=False)
                data = await r.json()
        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            raise ProviderError(self.name, 200, f"bad shape: {e}", retryable=False)
        usage = data.get("usageMetadata", {}) or {}
        return LLMResponse(text=text, provider=self.name, model=self.model, usage={
            "input": int(usage.get("promptTokenCount", 0)),
            "output": int(usage.get("candidatesTokenCount", 0)),
        })


class OpenAICompatibleProvider:
    """Works for Groq, DeepSeek, and any OpenAI-chat-compatible API."""
    name = "openai_compat"

    def __init__(self, name: str, model: str, api_key: str, base_url: str):
        self.name = name
        self.model = model
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    async def complete(self, prompt: str, *, max_tokens: int = 512, temperature: float = 0.0) -> LLMResponse:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        async with aiohttp.ClientSession() as s:
            async with s.post(url, headers=headers, json=body, timeout=aiohttp.ClientTimeout(total=30)) as r:
                txt = await r.text()
                if r.status in (429, 500, 502, 503, 504):
                    raise ProviderError(self.name, r.status, txt[:200], retryable=True)
                if r.status == 413:
                    raise ProviderError(self.name, r.status, "payload too large", retryable=False)
                if r.status in (401, 403):
                    raise ProviderError(self.name, r.status, f"auth: {txt[:120]}", retryable=False)
                if r.status != 200:
                    raise ProviderError(self.name, r.status, txt[:200], retryable=False)
                data = await r.json()
        try:
            text = data["choices"][0]["message"]["content"]
        except Exception as e:
            raise ProviderError(self.name, 200, f"bad shape: {e}", retryable=False)
        usage = data.get("usage", {}) or {}
        return LLMResponse(text=text, provider=self.name, model=self.model, usage={
            "input": int(usage.get("prompt_tokens", 0)),
            "output": int(usage.get("completion_tokens", 0)),
        })


def build_providers() -> list[LLMProvider]:
    providers: list[LLMProvider] = []

    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        providers.append(GeminiProvider(gemini_key))

    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        providers.append(OpenAICompatibleProvider("groq", "llama-3.1-8b-instant", groq_key, "https://api.groq.com/openai/v1"))

    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if deepseek_key:
        providers.append(OpenAICompatibleProvider("deepseek", "deepseek-chat", deepseek_key, "https://api.deepseek.com/v1"))

    return providers
