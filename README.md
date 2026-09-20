# Nexus Catalogue Intelligence — Web Scraping & Exploratory Analysis

**CodeAlpha Data Analytics Internship · Task 1 · Sajid Ali**

An end-to-end Python web-scraping project for the [Books to Scrape](https://books.toscrape.com/) training catalogue. The scraper navigates listing pages, opens product details, collects a structured book dataset, validates unique UPCs and generates an interactive dashboard plus a repeatable Markdown report.

> **Data integrity:** Books to Scrape explicitly states that this is a demonstration website and its prices and ratings are randomly assigned. The dashboard studies the extracted catalogue only; it makes no claims about actual sales, customers, demand or profit.

## Start here

1. Download and extract the ZIP.
2. Open **`OPEN_DASHBOARD.html`** in Chrome to explore the included **20-book, source-verified starter sample**. This is a **single self-contained HTML file** with its styling, code and data embedded, so it opens directly from disk or a mobile file viewer. Extract the ZIP first if your viewer does not support opening the HTML entry directly. The starter sample contains title, UPC, displayed price, available units and source URL. Its category and rating fields are blank because those fields were not verified in the included extraction.
3. To collect the fuller catalogue on Windows, double-click **`RUN_SCRAPER.bat`** while connected to the internet. It installs the two Python dependencies and runs the scraper. Python 3.9+ is required. The script writes updated files, rebuilds the standalone file, then opens it.

You can also run the commands manually in a terminal at the project root:

```bash
python -m pip install -r requirements.txt
python scrape.py
python analyze.py
```

If `python` is not recognized on Windows, try `py -3`. For a quick preview of the live pipeline, run `py -3 scrape.py --max-pages 2 --max-books 40`. The default attempts up to 50 catalogue pages and 1,000 product pages, so expect several minutes. It pauses between requests, uses retries for transient failures, and remains sequential.

## 📊 Interactive Dashboard Preview

<p align="center">
  <a href="https://sajidexpertise.github.io/Web-Scraping-and-Book-Catalogue-Analysis-Task-1-CodeAlpha/dashboard/">
    <img src="dashboard/dashboard.png"
         alt="Nexus Catalogue Intelligence Dashboard – CodeAlpha Task 1"
         width="100%">
  </a>
</p>

<p align="center">
  <strong>
    <a href="https://sajidexpertise.github.io/CodeAlpha-Web-Scraping-and-Book-Catalogue-Analysis-Task-1/">
      🚀 Open the Live Interactive Dashboard
    </a>
  </strong>
</p>

## What the scraper extracts

| CSV field | Meaning | Source |
| --- | --- | --- |
| `title` | Full book title | Product heading |
| `upc` | Stable identifier used for deduplication | Product information table |
| `price_gbp` | Displayed catalogue price in pounds | Product heading |
| `stock` | Displayed available units | Product availability text |
| `category` | Breadcrumb category | Product page navigation |
| `rating` | One-to-five star class, not a review score | Product CSS class |
| `url` | Direct source link | Listing to detail-page navigation |

The scraper follows the **Next** pagination link and each product card's URL, reads HTML with **BeautifulSoup**, handles timeouts/retries, validates key fields and deduplicates by UPC. A failed detail page is skipped and logged in `reports/skipped_pages.txt`; check `data/metadata.json` for the final skipped count. The provided starter sample is preserved if the run fails before collecting any rows.

## Files

```text
CodeAlpha_Book_Catalogue_Intelligence/
├── RUN_SCRAPER.bat             Windows one-click runner
├── OPEN_DASHBOARD.html         One-file mobile/offline dashboard
├── build_standalone.py         Regenerates one-file dashboard from source
├── scrape.py                   Requests + BeautifulSoup crawler
├── analyze.py                  Reproducible summary statistics
├── requirements.txt
├── data/
│   ├── books.csv               Dataset, starter sample until live scrape
│   └── metadata.json           Provenance, scope and collected date
├── dashboard/
│   ├── index.html              Editable Nexus layout and embedded responsive CSS
│   ├── app.js                   Filters, charts, export and table
│   └── data.js                  Dataset generated for file:// access
├── reports/
│   └── summary.md              Analysis recomputed from CSV
└── SUBMISSION.md               GitHub, LinkedIn and video guidance
```

The chosen Nexus dashboard's four headline figures and charts update together on each filter change. It includes a price-band histogram, price-versus-stock scatter, category and rating distributions, a ranked price list, and a paginated source-linked table. Search, price segment, category and stock filters update every view. Export downloads exactly the current filtered records. The initial sample has no verified category or rating values, so those panels explain the limitation until a live product-detail scrape fills them.

## Data scope and reproducibility

- **Included sample:** 20 linked product pages from the first catalogue listing, checked on 12 September 2026. The exact extraction hour was not recorded.
- **Live run:** Accesses the public site again, so current values or record counts may differ from the sample. The generated metadata records the UTC timestamp and scope.
- **Limitation:** This sandbox is for learning HTML parsing and analysis. Category/ratings in the starter sample are unavailable; do not interpret demo prices or ratings as genuine commercial signals. Displayed stock is a page value, not a transaction history.
- **Refresh:** Run `scrape.py` again. It overwrites `books.csv`, `metadata.json`, `dashboard/data.js`, `reports/summary.md` and `OPEN_DASHBOARD.html` after scraping. Reopen or refresh the HTML file afterward.
- **Editing:** Edit `dashboard/index.html` (layout and CSS) and `dashboard/app.js` (analytics and interactions) in VS Code. After changing them, run `python build_standalone.py` to regenerate `OPEN_DASHBOARD.html`. Opening only `dashboard/index.html` inside some ZIP viewers may block its data and JS files; use the standalone file on mobile.

## Task 1 requirement mapping

| CodeAlpha requirement | Project evidence |
| --- | --- |
| Use a Python scraping library | `scrape.py` uses BeautifulSoup and Requests |
| Collect data from public web pages | The site URL and each book's direct URL are stored |
| Navigate HTML accurately | Product cards, pagination, breadcrumbs, product table, CSS rating |
| Build a tailored custom dataset | `data/books.csv` has 7 analysis-ready fields |
| Analyze and report | `analyze.py`, `reports/summary.md`, offline dashboard |

**Suggested GitHub repository:** `CodeAlpha_Book_Catalogue_Intelligence`
