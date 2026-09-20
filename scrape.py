"""Scrape the Books to Scrape training catalogue into a reusable dataset."""
from __future__ import annotations

import argparse
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://books.toscrape.com/"
ROOT = Path(__file__).resolve().parent
RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": "CodeAlpha-Book-Catalogue-Study/1.0 (educational project)"})
    s.mount("https://", HTTPAdapter(max_retries=Retry(total=3, backoff_factor=.5, status_forcelist=[429, 500, 502, 503, 504])))
    return s


def money(text: str) -> float:
    match = re.search(r"\d+(?:\.\d+)?", text.replace("Â", ""))
    return float(match.group()) if match else 0.0


def listing_pages(max_pages: int, pause: float) -> list[dict]:
    s = session()
    found: list[dict] = []
    for page in range(1, max_pages + 1):
        url = urljoin(BASE_URL, f"catalogue/page-{page}.html")
        response = s.get(url, timeout=25)
        if response.status_code == 404:
            break
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select("article.product_pod")
        if not cards:
            break
        for card in cards:
            link = card.select_one("h3 a")
            rating_class = card.select_one("p.star-rating").get("class", ["", "One"])[-1]
            found.append({
                "title": link.get("title", "").strip(),
                "price": money(card.select_one("p.price_color").get_text(" ", strip=True)),
                "rating": RATINGS.get(rating_class, 0),
                "availability": card.select_one("p.instock.availability").get_text(" ", strip=True),
                "source_url": urljoin(url, link.get("href", "")),
                "listing_page": page,
            })
        print(f"Page {page}: {len(cards)} books (total {len(found)})")
        time.sleep(pause)
    return found


def detail(row: dict) -> dict:
    s = session()
    response = s.get(row["source_url"], timeout=25)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    table = {tr.th.get_text(strip=True): tr.td.get_text(" ", strip=True) for tr in soup.select("table.table tr")}
    breadcrumb = [a.get_text(" ", strip=True) for a in soup.select("ul.breadcrumb li a")]
    row.update({
        "upc": table.get("UPC", ""),
        "category": breadcrumb[-1] if breadcrumb else "Uncategorized",
        "price_excl_tax": money(table.get("Price (excl. tax)", "0")),
        "price_incl_tax": money(table.get("Price (incl. tax)", "0")),
        "tax": money(table.get("Tax", "0")),
        "available_units": int((re.search(r"\d+", table.get("Availability", "0")) or ["0"])[0]),
        "reviews": int(table.get("Number of reviews", "0") or 0),
    })
    return row


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape the public Books to Scrape training catalogue.")
    parser.add_argument("--max-pages", type=int, default=50, help="Listing pages to scrape (1–50).")
    parser.add_argument("--workers", type=int, default=12, help="Concurrent product-detail requests.")
    parser.add_argument("--pause", type=float, default=.08, help="Polite delay between listing pages.")
    parser.add_argument("--listing-only", action="store_true", help="Skip detail pages for a faster preview.")
    args = parser.parse_args()
    rows = listing_pages(max(1, min(args.max_pages, 50)), max(0, args.pause))
    if not args.listing_only:
        print(f"Collecting category, UPC and stock details with {args.workers} workers…")
        completed = []
        with ThreadPoolExecutor(max_workers=max(1, min(args.workers, 16))) as pool:
            jobs = {pool.submit(detail, row): row for row in rows}
            for number, future in enumerate(as_completed(jobs), 1):
                try:
                    completed.append(future.result())
                except Exception as exc:
                    fallback = jobs[future]
                    fallback.update({"upc": "", "category": "Uncategorized", "price_excl_tax": fallback["price"], "price_incl_tax": fallback["price"], "tax": 0, "available_units": 0, "reviews": 0, "detail_error": str(exc)})
                    completed.append(fallback)
                if number % 100 == 0 or number == len(rows):
                    print(f"Details: {number}/{len(rows)}")
        rows = sorted(completed, key=lambda x: (x["listing_page"], x["title"]))
    output = ROOT / "data" / "books.csv"
    output.parent.mkdir(exist_ok=True)
    pd.DataFrame(rows).drop_duplicates(subset=["upc"] if rows and rows[0].get("upc") else ["source_url"]).to_csv(output, index=False, encoding="utf-8-sig")
    print(f"Saved {len(rows):,} records to {output}")


if __name__ == "__main__":
    main()
