"""Reproducible descriptive analysis of the scraped demonstration catalogue."""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from statistics import mean, median

ROOT = Path(__file__).resolve().parent


def write_report(rows: list[dict], metadata: dict, path: Path) -> None:
    prices = [float(x["price_gbp"]) for x in rows]
    stocks = [int(x["stock"]) for x in rows]
    categories = Counter(x.get("category") or "Unclassified" for x in rows)
    high = max(rows, key=lambda x: float(x["price_gbp"]))
    low = min(rows, key=lambda x: float(x["price_gbp"]))
    rating_rows = [int(x["rating"]) for x in rows if str(x.get("rating", "")).strip()]
    lines = [
        "# Catalogue analysis",
        "",
        f"Source: {metadata['source']}  ",
        f"Collected (UTC): {metadata['collected_utc']}  ",
        f"Scope: {'starter sample from catalogue page 1' if metadata['sample'] else 'live scraper output'}; {len(rows)} distinct products.",
        "",
        "## Summary",
        "",
        f"- Distinct books: **{len(rows):,}**",
        f"- Average displayed price: **£{mean(prices):.2f}**; median: **£{median(prices):.2f}**",
        f"- Lowest displayed price: **£{float(low['price_gbp']):.2f}**, {low['title']}",
        f"- Highest displayed price: **£{float(high['price_gbp']):.2f}**, {high['title']}",
        f"- Displayed units available: **{sum(stocks):,}**; out-of-stock listings: **{sum(v == 0 for v in stocks)}**",
        f"- Categories represented: **{len(categories):,}**",
        f"- Average star rating: **{mean(rating_rows):.2f} / 5**" if rating_rows else "- Star ratings: **unavailable in the verified starter sample**",
        "",
        "## Largest categories by listing count",
        "",
        "| Category | Books | Share |",
        "| --- | ---: | ---: |",
    ]
    lines += [f"| {name.replace('|', '/')} | {count} | {100 * count / len(rows):.1f}% |" for name, count in categories.most_common(10)]
    lines += [
        "",
        "## Interpretation",
        "",
        "These figures describe the pages actually collected, not customer demand, sales, profit or conversion.",
        "The source is a demonstration site; its prices and ratings are randomly assigned and are not real business metrics.",
        ("The starter sample has no verified category/rating values; rerun the scraper to extract those fields from HTML."
         if metadata["sample"] else
         "Category and rating values come from product detail pages; inspect skipped pages for any missing records."),
        "When pages or product details fail, check reports/skipped_pages.txt and the metadata's skipped_products count.",
        "",
        "## Method",
        "",
        "Follow catalogue pagination, open each product page, parse title, price, availability, category and UPC,",
        "read the star-rating CSS class, deduplicate by UPC, and write CSV plus an offline dashboard dataset.",
    ]
    path.parent.mkdir(exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    with (ROOT / "data" / "books.csv").open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    metadata = json.loads((ROOT / "data" / "metadata.json").read_text(encoding="utf-8"))
    write_report(rows, metadata, ROOT / "reports" / "summary.md")
    print("Updated reports/summary.md")
