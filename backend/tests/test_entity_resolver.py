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
"""Unit test for entity resolver."""
import sys, asyncio
sys.path.insert(0, ".")

from app.services.entity_resolver import resolve, normalize_text


async def main():
    cases = [
        ("Open AI", "OpenAI"),
        ("OpenAI Inc.", "OpenAI"),
        ("Open-AI", "OpenAI"),
        ("Anthropic PBC", "Anthropic"),
        ("DeepMind", "Google DeepMind"),
        ("Facebook AI Research", "Meta"),
        ("FAIR", "Meta"),
        ("HF", "Hugging Face"),
        ("HuggingFace", "Hugging Face"),
        ("NVIDIA", "Nvidia"),
        ("MSFT", "Microsoft"),
        ("Some Random Startup XYZ", "Some Random Startup XYZ"),
        ("Mistral", "Mistral AI"),
    ]
    print(f"{'Input':<30} -> {'Canonical':<25} conf  method  reason")
    for raw, expected in cases:
        r = await resolve(raw)
        ok = "OK" if r.canonical == expected else "FAIL"
        print(f"  [{ok}] {raw:<28} -> {r.canonical:<23} {r.confidence:.2f}  {r.method:<8}  {r.reasoning[:60]}")
        assert r.canonical == expected, f"{raw} -> {r.canonical} (expected {expected})"

    # empty input
    r = await resolve("")
    assert r.canonical == "" and r.confidence == 0.0
    print("\nEmpty input handled correctly.")

    # normalize_text
    assert normalize_text("Open  AI, Inc.") == "open ai inc"
    assert normalize_text("  Hugging-Face!  ") == "hugging face"
    print("normalize_text works.")

    print("\nALL TESTS PASSED")


if __name__ == "__main__":
    asyncio.run(main())
