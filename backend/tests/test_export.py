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
"""Test CSV/TSV export formatting."""
import sys
from datetime import datetime, timezone
sys.path.insert(0, ".")

from types import SimpleNamespace
from app.services.export import to_csv, to_tsv


def make_paper():
    p = SimpleNamespace()
    p.id = 1
    p.source = "arxiv"
    p.source_id = "2609.04203"
    p.title = "Test Paper, with comma"
    p.authors_json = ["Alice Smith", "Bob Jones"]
    p.categories = ["cs.AI", "cs.LG"]
    p.url = "http://arxiv.org/abs/2609.04203"
    p.pdf_url = "http://arxiv.org/pdf/2609.04203"
    p.published_at = datetime(2026, 9, 3, tzinfo=timezone.utc)
    p.github_repo = None
    p.github_stars = None
    p.github_forks = None
    p.citations = None
    p.abstract = "Test abstract.\n\nWith a newline."
    p.created_at = datetime(2026, 9, 4, tzinfo=timezone.utc)
    return p


def main():
    paper = make_paper()

    csv_out = to_csv("papers", [paper])
    print("CSV:")
    print(csv_out)
    assert csv_out.startswith("id,source,source_id,title")
    assert '"Test Paper, with comma"' in csv_out  # comma gets quoted
    assert "Alice Smith; Bob Jones" in csv_out  # list joined
    print("CSV format: OK")

    print("\nTSV:")
    tsv_out = to_tsv("papers", [paper])
    print(tsv_out)
    assert tsv_out.startswith("id\tsource\tsource_id\ttitle")
    assert "\t" in tsv_out.split("\n")[1]  # tab-separated
    assert "\n\n" not in tsv_out  # newlines flattened
    print("TSV format: OK")

    print("\nALL EXPORT TESTS PASSED")


if __name__ == "__main__":
    main()
