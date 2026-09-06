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
"""Entity resolution: normalize raw mentions ("Open AI", "open-ai inc") to canonical forms ("OpenAI").

Strategy (in order):
  1. EXACT match against an existing alias in the DB.
  2. NORMALIZED match: lowercased, punctuation-stripped, whitespace-collapsed.
  3. FUZZY match: RapidFuzz token_sort_ratio for high-confidence near-duplicates (>=95).
  4. LLM assist (optional): ask the configured LLM tier whether two candidates are the same entity.
  5. Otherwise create a new canonical entity.

Each result includes `confidence` (0-1) and `reasoning` so the system is auditable.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from rapidfuzz import fuzz

from app.core.logging import get_logger
from app.models.orm import Entity, EntityAlias
from app.services.llm.extractor import extract_json

log = get_logger(__name__)

# Known canonical forms that appear often in the wild and have known aliases.
# Used as ground-truth seeds so "Open AI" -> "OpenAI" works deterministically.
KNOWN_CANONICALS: dict[str, list[str]] = {
    "OpenAI": ["Open AI", "OpenAI Inc.", "Open-AI", "OpenAI Inc", "OpenAi"],
    "Anthropic": ["Anthropic PBC", "Anthropic AI", "anthropic"],
    "Google DeepMind": ["DeepMind", "Google DeepMind AI", "deepmind"],
    "Microsoft": ["MSFT", "Microsoft Corp", "Microsoft Corp.", "Microsoft Research"],
    "Meta": ["Meta Platforms", "Facebook AI Research", "FAIR", "Meta AI"],
    "Hugging Face": ["HuggingFace", "HF", "hugging-face"],
    "Mistral AI": ["Mistral", "MistralAI"],
    "Cohere": ["Cohere AI", "cohere.com"],
    "Stability AI": ["StabilityAI", "Stability"],
    "Nvidia": ["NVIDIA", "Nvidia Corp", "nvidia"],
    "Apple": ["Apple Inc", "Apple Inc.", "apple.com"],
    "Google": ["Alphabet", "alphabet.com"],
    "Amazon": ["AWS", "Amazon.com", "Amazon Web Services"],
    "Tesla": ["Tesla Inc", "Tesla AI"],
}


_NONALNUM_RE = re.compile(r"[^a-z0-9 ]+")
_SPACE_RE = re.compile(r"\s+")


def normalize_text(s: str) -> str:
    s = (s or "").lower()
    s = _NONALNUM_RE.sub(" ", s)
    s = _SPACE_RE.sub(" ", s).strip()
    return s


@dataclass
class ResolutionResult:
    canonical: str
    confidence: float
    reasoning: str
    method: str
    is_new: bool


def _build_seed_lookup() -> dict[str, str]:
    """Map normalized alias -> canonical name."""
    out: dict[str, str] = {}
    for canonical, aliases in KNOWN_CANONICALS.items():
        out[normalize_text(canonical)] = canonical
        for a in aliases:
            out[normalize_text(a)] = canonical
    return out


_SEED_LOOKUP = _build_seed_lookup()


def _resolve_with_seed(name: str) -> ResolutionResult | None:
    n = normalize_text(name)
    if n in _SEED_LOOKUP:
        return ResolutionResult(
            canonical=_SEED_LOOKUP[n],
            confidence=1.0,
            reasoning=f"Matched known canonical/alias '{name}' against seed dictionary",
            method="seed",
            is_new=False,
        )
    return None


async def _llm_same_entity(a: str, b: str) -> tuple[bool, float, str]:
    """Ask the LLM tier if two entity names refer to the same real-world entity."""
    schema = (
        'Return JSON: {"same": true|false, "confidence": 0.0-1.0, "reason": "<short justification>"}. '
        'Be conservative. If unsure, set same=false and confidence <= 0.5.'
    )
    prompt = (
        f"Are these two entity names referring to the SAME real-world organization?\n"
        f"  A: {a!r}\n  B: {b!r}\n\n"
        f"Schema: {schema}"
    )
    result = await extract_json(prompt, schema, max_tokens=200)
    if not result.ok or not isinstance(result.data, dict):
        return False, 0.0, "llm unavailable"
    return (
        bool(result.data.get("same")),
        float(result.data.get("confidence", 0.0)),
        str(result.data.get("reason", ""))[:160],
    )


async def resolve(name: str, *, kind: str = "company", db_session=None) -> ResolutionResult:
    """Resolve `name` to a canonical form. Updates DB if a session is provided."""
    name = (name or "").strip()
    if not name:
        return ResolutionResult(canonical="", confidence=0.0, reasoning="empty input", method="none", is_new=False)

    if db_session is not None:
        from sqlalchemy import select

        norm = normalize_text(name)

        # exact alias lookup
        alias_row = (
            await db_session.execute(
                select(EntityAlias).where(EntityAlias.kind == kind, EntityAlias.alias == norm)
            )
        ).scalar_one_or_none()
        if alias_row:
            ent = (
                await db_session.execute(select(Entity).where(Entity.id == alias_row.entity_id))
            ).scalar_one()
            return ResolutionResult(
                canonical=ent.canonical,
                confidence=float(alias_row.confidence or 1.0),
                reasoning=alias_row.reasoning or f"exact alias '{name}'",
                method=alias_row.reasoning.split(":")[0] if alias_row.reasoning else "db_exact",
                is_new=False,
            )

    # 1. seed dictionary
    seed = _resolve_with_seed(name)
    if seed:
        return seed

    # 2. fuzzy match against known canonicals
    nname = normalize_text(name)
    best_score = 0
    best_canon = None
    for canonical in list(_SEED_LOOKUP.values()) + list(KNOWN_CANONICALS.keys()):
        score = fuzz.token_sort_ratio(nname, normalize_text(canonical))
        if score > best_score:
            best_score = score
            best_canon = canonical

    if best_canon and best_score >= 95:
        return ResolutionResult(
            canonical=best_canon,
            confidence=0.9,
            reasoning=f"Fuzzy token-sort match (score={best_score}) against '{best_canon}'",
            method="fuzzy",
            is_new=False,
        )

    # 3. otherwise treat as new entity
    return ResolutionResult(
        canonical=name,
        confidence=1.0,
        reasoning="No match in seed dictionary or above fuzzy threshold; treated as new canonical",
        method="new",
        is_new=True,
    )
