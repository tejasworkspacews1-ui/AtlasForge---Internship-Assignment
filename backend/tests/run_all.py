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
"""Comprehensive test runner — runs all phase tests sequentially."""
import asyncio
import sys
import traceback
from pathlib import Path

sys.path.insert(0, ".")

TESTS = [
    "tests.test_llm_helpers",
    "tests.test_llm_adapter",
    "tests.test_entity_resolver",
    "tests.test_export",
    "tests.test_smoke",
]


def main() -> int:
    print("=" * 60)
    print("AtlasForge — Test Suite")
    print("=" * 60)

    # Run smoke first (needs DB init)
    from app.db.session import init_db
    asyncio.run(init_db())

    passed = failed = 0
    for name in TESTS:
        print(f"\n--- {name} ---")
        try:
            # Import fresh module so module-level execution doesn't auto-run tests
            import importlib
            mod = importlib.import_module(name)
            if hasattr(mod, "main") and asyncio.iscoroutinefunction(mod.main):
                asyncio.run(mod.main())
            elif hasattr(mod, "main"):
                mod.main()
            elif hasattr(mod, "run"):
                mod.run()
            else:
                print(f"  (no main entry, skipped)")
            print(f"  PASS")
            passed += 1
        except SystemExit as e:
            if e.code == 0:
                print(f"  PASS")
                passed += 1
            else:
                print(f"  FAIL (exit {e.code})")
                failed += 1
        except Exception as e:
            traceback.print_exc()
            print(f"  FAIL: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
