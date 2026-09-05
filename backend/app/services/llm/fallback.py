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
"""Deterministic, rule-based extractor — used when no LLM API keys are configured.

This is NOT a fabrication. It only extracts signals that can be detected with
high confidence from the text itself (capitalized noun phrases, URLs, hashtags,
email patterns). Anything ambiguous is omitted. Always returns a structured
result with `method: "deterministic"` so downstream systems can tell it apart
from LLM output.
"""
from __future__ import annotations

import re
from typing import Any

from app.core.logging import get_logger

log = get_logger(__name__)

_ORG_HINT_RE = re.compile(
    r"\b([A-Z][\w&]+(?:\s+[A-Z][\w&]+){0,3})\b(?:\s+(?:Inc|LLC|Ltd|Corp|Corporation|AI|Labs|Technologies|Group|Studios)\b)?"
)
_URL_RE = re.compile(r"https?://[^\s)\]\"'>]+")
_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
_HASHTAG_RE = re.compile(r"#[\w]{2,}")
_MONEY_RE = re.compile(r"\$\s?(\d{1,3}(?:[,.]\d{3})*|\d+)(?:\s?(million|billion|M|B|k|K))?", re.IGNORECASE)

GENERIC_ORG_BLACKLIST = {
    "The", "This", "That", "These", "Those", "We", "They", "It",
    "Our", "Your", "His", "Her", "Its", "And", "But", "Or", "For",
    "With", "From", "Into", "Over", "Under", "Above",
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
    "USA", "UK", "EU", "AI", "ML", "LLM",
}


def extract(text: str, *, max_orgs: int = 10, max_urls: int = 10) -> dict[str, Any]:
    if not text:
        return {"method": "deterministic", "organizations": [], "urls": [], "emails": [], "hashtags": [], "money_mentions": []}

    orgs = []
    seen = set()
    for m in _ORG_HINT_RE.finditer(text):
        name = m.group(1).strip()
        if name in GENERIC_ORG_BLACKLIST or len(name) < 2:
            continue
        if name in seen:
            continue
        seen.add(name)
        orgs.append({"name": name, "confidence": 0.6, "source": "titlecase_heuristic"})
        if len(orgs) >= max_orgs:
            break

    urls = []
    for m in _URL_RE.finditer(text):
        u = m.group(0).rstrip(".,;:")
        if u not in urls:
            urls.append(u)
        if len(urls) >= max_urls:
            break

    emails = list(dict.fromkeys(_EMAIL_RE.findall(text)))[:5]
    hashtags = list(dict.fromkeys(_HASHTAG_RE.findall(text)))[:10]
    money = []
    for m in _MONEY_RE.finditer(text):
        money.append({"raw": m.group(0), "amount": m.group(1), "unit": (m.group(2) or "").lower() or None})

    return {
        "method": "deterministic",
        "organizations": orgs,
        "urls": urls,
        "emails": emails,
        "hashtags": hashtags,
        "money_mentions": money[:5],
    }
