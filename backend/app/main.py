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
"""FastAPI application factory."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_core import router as core_router
from app.api.routes_data import router as data_router
from app.api.routes_pipeline import router as pipeline_router
from app.api.routes_ingest import router as ingest_router
from app.api.routes_llm import router as llm_router
from app.api.routes_entities import router as entities_router
from app.api.routes_export import router as export_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(core_router)
    app.include_router(data_router)
    app.include_router(pipeline_router)
    app.include_router(ingest_router)
    app.include_router(llm_router)
    app.include_router(entities_router)
    app.include_router(export_router)
    return app


app = create_app()
