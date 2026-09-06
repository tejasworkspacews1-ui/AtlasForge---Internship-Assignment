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
"""Full HTTP smoke test via FastAPI ASGI transport (no live server needed)."""
import asyncio
import sys
sys.path.insert(0, ".")

from httpx import ASGITransport, AsyncClient

from app.main import create_app
from app.db.session import init_db


async def main() -> None:
    await init_db()
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        # core
        r = await c.get("/api/health")
        assert r.status_code == 200
        print("health: OK")

        r = await c.get("/api/dashboard")
        assert r.status_code == 200
        d = r.json()
        assert "total_records" in d
        print(f"dashboard: total={d['total_records']} OK")

        # modules
        for m in ["papers", "startups", "products", "news", "jobs"]:
            r = await c.get(f"/api/{m}?page=1&page_size=5")
            assert r.status_code == 200
            print(f"{m}: OK")

        # pipeline
        r = await c.get("/api/pipeline/runs")
        assert r.status_code == 200
        print(f"pipeline: {r.json()['total']} runs OK")

        # ingest available
        r = await c.get("/api/ingest/available")
        assert r.status_code == 200
        ingests = r.json()
        assert "arxiv" in ingests
        print(f"ingest available: {list(ingests)} OK")

        # LLM
        r = await c.get("/api/llm/status")
        assert r.status_code == 200
        s = r.json()
        print(f"llm: {len(s['configured'])} providers configured OK")

        # entities
        r = await c.get("/api/entities/clusters?page_size=5")
        assert r.status_code == 200
        print(f"entities: {r.json()['total']} clusters OK")

        r = await c.post("/api/entities/resolve", json={"name": "Open AI"})
        assert r.status_code == 200
        out = r.json()
        assert out["canonical"] == "OpenAI"
        print(f"resolve: {out['canonical']} ({out['method']}) OK")

        # export
        r = await c.get("/api/export/available")
        assert r.status_code == 200
        print(f"export available: {r.json()['modules']} OK")

        for m in ["papers", "news", "jobs", "entities"]:
            r = await c.get(f"/api/export/{m}.csv?limit=3")
            assert r.status_code == 200
            assert r.headers["content-type"].startswith("text/csv")
            print(f"export {m}.csv: {len(r.text)} bytes OK")

            r = await c.get(f"/api/export/{m}.tsv?limit=3")
            assert r.status_code == 200
            assert r.headers["content-type"].startswith("text/tab-separated")
            print(f"export {m}.tsv: {len(r.text)} bytes OK")

        # unknown module should 404
        r = await c.get("/api/export/bogus.csv")
        assert r.status_code == 404
        print("export 404: OK")

    print("\nALL SMOKE TESTS PASSED")


if __name__ == "__main__":
    asyncio.run(main())
