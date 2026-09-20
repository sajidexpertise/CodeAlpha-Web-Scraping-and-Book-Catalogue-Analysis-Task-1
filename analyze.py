"""Create concise quality and catalogue summaries from the scraped dataset."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
source = ROOT / "data" / "books.csv"
report_dir = ROOT / "reports"
report_dir.mkdir(exist_ok=True)

df = pd.read_csv(source)
summary = pd.DataFrame([
    {"metric": "records", "value": len(df)},
    {"metric": "unique_titles", "value": df.get("title", pd.Series(dtype=str)).nunique()},
    {"metric": "average_price_gbp", "value": round(pd.to_numeric(df.get("price"), errors="coerce").mean(), 2)},
    {"metric": "duplicate_source_urls", "value": df.get("source_url", pd.Series(dtype=str)).duplicated().sum()},
    {"metric": "missing_values", "value": int(df.isna().sum().sum())},
])
summary.to_csv(report_dir / "catalogue_summary.csv", index=False)

if "category" in df:
    df.groupby("category", dropna=False).agg(books=("title", "count"), average_price_gbp=("price", "mean")).sort_values("books", ascending=False).round(2).to_csv(report_dir / "category_summary.csv")
if "rating" in df:
    df.groupby("rating", dropna=False).size().rename("books").to_csv(report_dir / "rating_summary.csv")
print(summary.to_string(index=False))
print(f"Reports saved in {report_dir}")
