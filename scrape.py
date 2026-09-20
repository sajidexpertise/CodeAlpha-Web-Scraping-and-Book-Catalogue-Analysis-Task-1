"""Polite catalogue scraper for the public Books to Scrape training sandbox."""
from __future__ import annotations

import argparse
import csv
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from analyze import write_report
from build_standalone import build

ROOT = Path(__file__).resolve().parent
SITE = "https://books.toscrape.com/"
FIELDS = ("title", "upc", "price_gbp", "stock", "category", "rating", "url")
RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def soup_for(session: requests.Session, url: str) -> BeautifulSoup:
    if urlparse(url).netloc != "books.toscrape.com":
        raise ValueError(f"Unexpected domain: {url}")
    response = session.get(url, timeout=(8, 25))
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")


def require(node, label: str):
    if node is None:
        raise ValueError(f"Missing expected HTML element: {label}")
    return node


def extract_product(soup: BeautifulSoup, url: str, listing_rating: int) -> dict:
    title = require(soup.select_one(".product_main h1"), "product title").get_text(" ", strip=True)
    price_text = require(soup.select_one(".product_main .price_color"), "price").get_text(strip=True)
    price = float(re.search(r"\d+(?:\.\d+)?", price_text).group())
    availability = require(soup.select_one(".product_main .availability"), "availability").get_text(" ", strip=True)
    quantity = re.search(r"\((\d+) available\)", availability)
    stock = int(quantity.group(1)) if quantity else 0
    breadcrumb = soup.select("ul.breadcrumb li")
    category = breadcrumb[-2].get_text(" ", strip=True) if len(breadcrumb) >= 4 else "Unclassified"
    information = {
        tr.select_one("th").get_text(" ", strip=True): tr.select_one("td").get_text(" ", strip=True)
        for tr in soup.select("table.table-striped tr")
        if tr.select_one("th") and tr.select_one("td")
    }
    upc = information.get("UPC", "")
    if not upc:
        raise ValueError(f"Missing UPC on {url}")
    rating_node = soup.select_one(".product_main .star-rating")
    rating = next((RATINGS[c] for c in rating_node.get("class", []) if c in RATINGS), listing_rating) if rating_node else listing_rating
    return {
        "title": title, "upc": upc, "price_gbp": round(price, 2),
        "stock": stock, "category": category, "rating": rating, "url": url,
    }


def scrape(max_pages: int, max_books: int, delay: float) -> tuple[list[dict], int, list[str]]:
    session = requests.Session()
    session.headers["User-Agent"] = "CodeAlphaCatalogueStudy/1.0 (educational, polite sequential requests)"
    retry = Retry(total=3, backoff_factor=0.8, status_forcelist=(429, 500, 502, 503, 504))
    session.mount("https://", HTTPAdapter(max_retries=retry))
    records, errors, visited = [], [], set()
    listing_url, pages = SITE, 0
    try:
        while listing_url and pages < max_pages and len(records) < max_books:
            if listing_url in visited:
                raise RuntimeError("Pagination cycle detected")
            visited.add(listing_url)
            listing = soup_for(session, listing_url)
            pages += 1
            cards = listing.select("article.product_pod")
            if not cards:
                raise RuntimeError(f"No catalogue cards found on {listing_url}; check site layout")
            print(f"Page {pages}: {len(cards)} books")
            for card in cards:
                if len(records) >= max_books:
                    break
                link = require(card.select_one("h3 a[href]"), "book link")
                book_url = urljoin(listing_url, link["href"])
                star = card.select_one(".star-rating")
                listing_rating = next((RATINGS[c] for c in star.get("class", []) if c in RATINGS), 0) if star else 0
                try:
                    item = extract_product(soup_for(session, book_url), book_url, listing_rating)
                    records.append(item)
                except (requests.RequestException, ValueError, AttributeError) as exc:
                    errors.append(f"{book_url}: {exc}")
                    print(f"  Skipped {book_url}: {exc}")
                time.sleep(delay)
            next_link = listing.select_one("li.next a[href]")
            listing_url = urljoin(listing_url, next_link["href"]) if next_link else None
            time.sleep(delay)
    finally:
        session.close()
    unique = {row["upc"]: row for row in records}
    return list(unique.values()), pages, errors


def save(rows: list[dict], pages: int, errors: list[str]) -> None:
    if not rows:
        raise RuntimeError("No records scraped; starter files were preserved")
    (ROOT / "data").mkdir(exist_ok=True)
    out = ROOT / "data" / "books.csv"
    with out.with_suffix(".csv.tmp").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    out.with_suffix(".csv.tmp").replace(out)
    metadata = {
        "source": SITE, "sample": False, "record_count": len(rows),
        "pages_visited": pages, "skipped_products": len(errors),
        "collected_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (ROOT / "data" / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    # A JavaScript assignment loads directly from file:// without a local web server.
    payload = "window.CATALOGUE = " + json.dumps({"metadata": metadata, "records": rows}, ensure_ascii=False) + ";\n"
    (ROOT / "dashboard" / "data.js").write_text(payload, encoding="utf-8")
    write_report(rows, metadata, ROOT / "reports" / "summary.md")
    build()
    if errors:
        (ROOT / "reports" / "skipped_pages.txt").write_text("\n".join(errors) + "\n", encoding="utf-8")
    else:
        (ROOT / "reports" / "skipped_pages.txt").unlink(missing_ok=True)
    print(f"Saved {len(rows)} unique records across {pages} pages. Skipped: {len(errors)}.")
    print("Open OPEN_DASHBOARD.html in Chrome to explore the updated data.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape the Books to Scrape training catalogue")
    parser.add_argument("--max-pages", type=int, default=50, help="Catalogue pages (1 to 50)")
    parser.add_argument("--max-books", type=int, default=1000, help="Maximum products")
    parser.add_argument("--delay", type=float, default=0.2, help="Pause between requests, seconds")
    args = parser.parse_args()
    if not 1 <= args.max_pages <= 50 or args.max_books < 1 or args.delay < 0:
        parser.error("Use 1–50 pages, at least 1 book and a nonnegative delay")
    rows, pages, errors = scrape(args.max_pages, args.max_books, args.delay)
    save(rows, pages, errors)


if __name__ == "__main__":
    main()
