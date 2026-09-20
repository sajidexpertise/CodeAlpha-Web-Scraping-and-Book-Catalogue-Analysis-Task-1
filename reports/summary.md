# Catalogue analysis

Source: https://books.toscrape.com/  
Collected (UTC): 2026-09-19T15:09:53+00:00  
Scope: live scraper output; 1000 distinct products.

## Summary

- Distinct books: **1,000**
- Average displayed price: **£35.07**; median: **£35.98**
- Lowest displayed price: **£10.00**, An Abundance of Katherines
- Highest displayed price: **£59.99**, The Perfect Play (Play by Play #1)
- Displayed units available: **8,585**; out-of-stock listings: **0**
- Categories represented: **50**
- Average star rating: **2.92 / 5**

## Largest categories by listing count

| Category | Books | Share |
| --- | ---: | ---: |
| Default | 152 | 15.2% |
| Nonfiction | 110 | 11.0% |
| Sequential Art | 75 | 7.5% |
| Add a comment | 67 | 6.7% |
| Fiction | 65 | 6.5% |
| Young Adult | 54 | 5.4% |
| Fantasy | 48 | 4.8% |
| Romance | 35 | 3.5% |
| Mystery | 32 | 3.2% |
| Food and Drink | 30 | 3.0% |

## Interpretation

These figures describe the pages actually collected, not customer demand, sales, profit or conversion.
The source is a demonstration site; its prices and ratings are randomly assigned and are not real business metrics.
Category and rating values come from product detail pages; inspect skipped pages for any missing records.
When pages or product details fail, check reports/skipped_pages.txt and the metadata's skipped_products count.

## Method

Follow catalogue pagination, open each product page, parse title, price, availability, category and UPC,
read the star-rating CSS class, deduplicate by UPC, and write CSV plus an offline dashboard dataset.
