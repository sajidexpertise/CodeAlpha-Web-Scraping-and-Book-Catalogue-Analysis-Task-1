"""Embed the latest CSV in data.js so the dashboard also works from file://."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parent
source = ROOT / "data" / "books.csv"
target = ROOT / "dashboard" / "data.js"

if not source.exists():
    raise SystemExit("data/books.csv was not found. Run scrape.py first.")

frame = pd.read_csv(source).fillna("")
records = frame.to_dict(orient="records")
target.write_text("window.BOOK_DATA = " + json.dumps(records, ensure_ascii=False) + ";\n", encoding="utf-8")
print(f"Embedded {len(records):,} records in {target}")
