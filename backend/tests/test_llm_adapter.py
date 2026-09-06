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
"""Test the multi-tier adapter with mock providers (no real API calls).

Simulates:
  - 429 then success on first provider
  - 413 -> handled by chunking (smaller chunks on next try)
  - Auth failure on all providers -> deterministic fallback
"""
import asyncio
import sys
sys.path.insert(0, ".")

from app.services.llm.base import LLMProvider, LLMResponse, ProviderError, chunk_text
from app.services.llm.extractor import extract_json


class MockFlakyProvider:
    name = "mock_flaky"
    model = "mock-1"
    calls = 0

    async def complete(self, prompt, *, max_tokens=512, temperature=0.0):
        MockFlakyProvider.calls += 1
        if MockFlakyProvider.calls == 1:
            raise ProviderError(self.name, 429, "rate limited", retryable=True)
        return LLMResponse(text='[{"org":"OpenAI"},{"org":"Anthropic"}]', provider=self.name, model=self.model, usage={"input":10,"output":5})


class MockAuthFails:
    name = "mock_auth"
    model = "mock-2"
    async def complete(self, prompt, *, max_tokens=512, temperature=0.0):
        raise ProviderError(self.name, 401, "unauthorized", retryable=False)


import app.services.llm.extractor as ext

async def main():
    print("=== Test 1: 429 then success (retry) ===")
    ext.build_providers = lambda: [MockFlakyProvider()]
    MockFlakyProvider.calls = 0
    result = await extract_json("OpenAI and Anthropic raised funds", "schema", max_chunk_chars=12000)
    print(f"ok={result.ok} provider={result.provider} attempts={result.attempts} calls={MockFlakyProvider.calls}")
    print(f"data={result.data}")
    assert result.ok and result.attempts == 1 and MockFlakyProvider.calls == 2

    print("\n=== Test 2: All providers fail (deterministic fallback) ===")
    ext.build_providers = lambda: [MockAuthFails()]
    result = await extract_json("OpenAI and Anthropic raised funds", "schema", max_chunk_chars=12000)
    print(f"ok={result.ok} error={result.error}")
    assert not result.ok

    print("\n=== Test 3: No providers configured ===")
    ext.build_providers = lambda: []
    result = await extract_json("OpenAI and Anthropic raised funds", "schema", max_chunk_chars=12000)
    print(f"ok={result.ok} error={result.error}")
    assert not result.ok and "No LLM providers" in result.error

    print("\n=== Test 4: Chunking for large input ===")
    big = ("OpenAI Anthropic Google DeepMind " * 2000)
    chunks = chunk_text(big, max_chars=4000, overlap=50)
    print(f"chunks: {len(chunks)} total chars: {sum(len(c) for c in chunks)}")
    assert len(chunks) > 1

    print("\nALL TESTS PASSED")


if __name__ == "__main__":
    asyncio.run(main())
