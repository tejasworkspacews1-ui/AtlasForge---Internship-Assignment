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
"""Pydantic response/request schemas (Postgres-compatible API contract)."""
from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PaperOut(APIModel):
    id: int
    source: str
    title: str
    authors: list[str] = Field(default_factory=list, alias="authors_json")
    abstract: str | None = None
    categories: list[str] = Field(default_factory=list)
    url: str
    pdf_url: str | None = None
    published_at: datetime | None = None
    github_repo: str | None = None
    github_stars: int | None = None
    github_forks: int | None = None
    citations: int | None = None


class StartupOut(APIModel):
    id: int
    source: str
    name: str
    slug: str | None = None
    description: str | None = None
    website: str | None = None
    focus_area: str | None = None
    stage: str | None = None
    funding_usd: float | None = None
    location: str | None = None
    founded_year: int | None = None


class ProductOut(APIModel):
    id: int
    source: str
    name: str
    company: str | None = None
    category: str | None = None
    description: str | None = None
    url: str | None = None
    launched_at: datetime | None = None
    pricing_model: str | None = None


class NewsOut(APIModel):
    id: int
    source: str
    title: str
    url: str
    summary: str | None = None
    author: str | None = None
    published_at: datetime | None = None
    categories: list[str] = Field(default_factory=list)
    extracted: dict | None = None


class JobOut(APIModel):
    id: int
    source: str
    title: str
    company: str | None = None
    location: str | None = None
    remote: bool = False
    url: str
    description: str | None = None
    posted_at: datetime | None = None
    salary_min: float | None = None
    salary_max: float | None = None


class PipelineRunOut(APIModel):
    id: int
    run_id: str
    module: str
    source: str
    status: str
    started_at: datetime
    finished_at: datetime | None = None
    records_fetched: int
    records_new: int
    records_updated: int
    records_failed: int
    message: str | None = None


class ModuleCounts(BaseModel):
    papers: int = 0
    startups: int = 0
    products: int = 0
    news: int = 0
    jobs: int = 0


class DashboardMetricsOut(BaseModel):
    total_records: int
    records_last_24h: int
    pipeline_health: float
    freshness_score: float
    by_module: ModuleCounts


class PageResult(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
