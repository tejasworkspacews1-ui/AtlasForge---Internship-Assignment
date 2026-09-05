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
"""Quick unit test for LLM helper functions."""
import sys
sys.path.insert(0, ".")

from app.services.llm.base import chunk_text, merge_json_chunks, safe_json_parse

big = ("OpenAI announced a new model. " * 1000)
chunks = chunk_text(big, max_chars=5000, overlap=100)
print(f"chunks: {len(chunks)} sizes: {[len(c) for c in chunks]}")

merged = merge_json_chunks(['[{"a":1}]', '[{"b":2}]', '[{"c":3}]'])
print(f"merged: {merged}")

parsed = safe_json_parse("```json\n{\"x\":1}\n```")
print(f"parsed fences: {parsed}")

parsed2 = safe_json_parse('here is {"y":2} some prose')
print(f"parsed mid: {parsed2}")

from app.services.llm.fallback import extract as fb_extract
out = fb_extract("OpenAI raised $10B from Microsoft. Contact team@openai.com or visit https://openai.com #AI")
print(f"fallback: {out}")
