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
"""CSV / TSV serializers + per-module export column definitions.

CSV: comma-separated, RFC 4180 quoted.
TSV: tab-separated, single-line per row, no quoting — Google Sheets pastes cleanly.
"""
from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from typing import Any

# Column definitions: (column header, value extractor, JSON-safe default)
# Keep these narrow & spreadsheet-friendly. Datetimes -> ISO 8601 UTC.
MODULE_COLUMNS: dict[str, list[tuple[str, Any, Any]]] = {
    "papers": [
        ("id", lambda p: p.id, ""),
        ("source", lambda p: p.source, ""),
        ("source_id", lambda p: p.source_id, ""),
        ("title", lambda p: p.title, ""),
        ("authors", lambda p: "; ".join(p.authors_json or []), ""),
        ("categories", lambda p: "; ".join(p.categories or []), ""),
        ("url", lambda p: p.url, ""),
        ("pdf_url", lambda p: p.pdf_url, ""),
        ("published_at", lambda p: _iso(p.published_at), ""),
        ("github_repo", lambda p: p.github_repo, ""),
        ("github_stars", lambda p: p.github_stars, 0),
        ("github_forks", lambda p: p.github_forks, 0),
        ("citations", lambda p: p.citations, 0),
        ("abstract", lambda p: _clean(p.abstract), ""),
        ("created_at", lambda p: _iso(p.created_at), ""),
    ],
    "startups": [
        ("id", lambda p: p.id, ""),
        ("source", lambda p: p.source, ""),
        ("name", lambda p: p.name, ""),
        ("slug", lambda p: p.slug, ""),
        ("description", lambda p: _clean(p.description), ""),
        ("website", lambda p: p.website, ""),
        ("focus_area", lambda p: p.focus_area, ""),
        ("stage", lambda p: p.stage, ""),
        ("funding_usd", lambda p: p.funding_usd, 0),
        ("location", lambda p: p.location, ""),
        ("founded_year", lambda p: p.founded_year, ""),
    ],
    "products": [
        ("id", lambda p: p.id, ""),
        ("source", lambda p: p.source, ""),
        ("name", lambda p: p.name, ""),
        ("company", lambda p: p.company, ""),
        ("category", lambda p: p.category, ""),
        ("description", lambda p: _clean(p.description), ""),
        ("url", lambda p: p.url, ""),
        ("launched_at", lambda p: _iso(p.launched_at), ""),
        ("pricing_model", lambda p: p.pricing_model, ""),
    ],
    "news": [
        ("id", lambda p: p.id, ""),
        ("source", lambda p: p.source, ""),
        ("title", lambda p: p.title, ""),
        ("url", lambda p: p.url, ""),
        ("author", lambda p: p.author, ""),
        ("published_at", lambda p: _iso(p.published_at), ""),
        ("categories", lambda p: "; ".join(p.categories or []), ""),
        ("summary", lambda p: _clean(p.summary), ""),
        ("extracted_method", lambda p: (p.extracted or {}).get("method") if p.extracted else None, ""),
        ("created_at", lambda p: _iso(p.created_at), ""),
    ],
    "jobs": [
        ("id", lambda p: p.id, ""),
        ("source", lambda p: p.source, ""),
        ("title", lambda p: p.title, ""),
        ("company", lambda p: p.company, ""),
        ("location", lambda p: p.location, ""),
        ("remote", lambda p: bool(p.remote), ""),
        ("url", lambda p: p.url, ""),
        ("posted_at", lambda p: _iso(p.posted_at), ""),
        ("salary_min", lambda p: p.salary_min, ""),
        ("salary_max", lambda p: p.salary_max, ""),
        ("description", lambda p: _clean(p.description), ""),
    ],
    "entities": [
        ("id", lambda e: e.id, ""),
        ("kind", lambda e: e.kind, ""),
        ("canonical", lambda e: e.canonical, ""),
        ("confidence", lambda e: e.confidence, 0),
        ("alias_count", lambda e: len(e.aliases or []), 0),
    ],
}


def _iso(dt: datetime | None) -> str:
    if not dt:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()


def _clean(s: str | None) -> str:
    if not s:
        return ""
    # strip HTML tags crudely, normalize newlines
    import re

    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    # avoid breaking CSV by replacing newlines inside cells (already collapsed, but safety)
    s = s.replace("\t", " ").replace("\r", " ")
    return s


def to_csv(module: str, rows: list[Any]) -> str:
    cols = MODULE_COLUMNS[module]
    buf = io.StringIO()
    writer = csv.writer(buf, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    writer.writerow([c[0] for c in cols])
    for r in rows:
        writer.writerow([_safe(c[1](r)) for c in cols])
    return buf.getvalue()


def to_tsv(module: str, rows: list[Any]) -> str:
    """Tab-separated; newlines/tabs inside cells are stripped so Sheets pastes cleanly."""
    cols = MODULE_COLUMNS[module]
    out_lines: list[str] = []
    out_lines.append("\t".join(c[0] for c in cols))
    for r in rows:
        cells = []
        for c in cols:
            v = _safe(c[1](r))
            # Replace any tab/newline with space to keep one row = one line
            if isinstance(v, str):
                v = v.replace("\t", " ").replace("\n", " ").replace("\r", " ")
            cells.append(str(v))
        out_lines.append("\t".join(cells))
    return "\n".join(out_lines)


def _safe(v: Any) -> Any:
    if v is None:
        return ""
    if isinstance(v, datetime):
        return _iso(v)
    return v
