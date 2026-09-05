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
"""Smoke test: app boots, tables create, /health responds."""
import asyncio
from httpx import ASGITransport, AsyncClient

from app.main import create_app
from app.db.session import init_db


async def main() -> None:
    await init_db()
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/api/health")
        assert r.status_code == 200, r.text
        print("health:", r.json())
        r = await c.get("/api/dashboard")
        assert r.status_code == 200, r.text
        print("dashboard:", r.json())
        r = await c.get("/api/papers?page=1&page_size=5")
        assert r.status_code == 200, r.text
        print("papers:", r.json())


if __name__ == "__main__":
    asyncio.run(main())
