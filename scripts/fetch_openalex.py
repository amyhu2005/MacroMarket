"""
Fetch all works (papers) from the top-5 economics journals for the last 4
complete calendar years via the OpenAlex API, and cache the raw JSON pages.

Usage:
    python scripts/fetch_openalex.py
"""
import json
import time
from pathlib import Path

import requests

MAILTO = "strt.fkng.writing@gmail.com"  # for OpenAlex's polite pool (higher rate limit)
YEARS = [2022, 2023, 2024, 2025]
PER_PAGE = 200

JOURNALS = {
    "AER": "S23254222",
    "Econometrica": "S95464858",
    "JPE": "S95323914",
    "QJE": "S203860005",
    "ReStud": "S88935262",
}

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://api.openalex.org/works"


def fetch_journal(name: str, source_id: str) -> int:
    year_filter = "|".join(str(y) for y in YEARS)
    filter_str = f"primary_location.source.id:{source_id},publication_year:{year_filter},type:article"
    cursor = "*"
    page_num = 0
    total_fetched = 0

    while cursor:
        out_path = RAW_DIR / f"{name}_{page_num:03d}.json"
        if out_path.exists():
            # already cached; read it to recover the next cursor and count
            with open(out_path) as f:
                data = json.load(f)
        else:
            params = {
                "filter": filter_str,
                "per-page": PER_PAGE,
                "cursor": cursor,
                "mailto": MAILTO,
            }
            resp = requests.get(BASE_URL, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            with open(out_path, "w") as f:
                json.dump(data, f)
            time.sleep(0.1)  # be polite

        n = len(data["results"])
        total_fetched += n
        print(f"  {name} page {page_num}: {n} works (running total {total_fetched}/{data['meta']['count']})")

        cursor = data["meta"].get("next_cursor")
        page_num += 1
        if n == 0:
            break

    return total_fetched


def main():
    print(f"Fetching OpenAlex works for {len(JOURNALS)} journals, years {YEARS[0]}-{YEARS[-1]}")
    grand_total = 0
    for name, source_id in JOURNALS.items():
        print(f"\n{name} ({source_id}):")
        grand_total += fetch_journal(name, source_id)
    print(f"\nDone. Total papers fetched: {grand_total}")


if __name__ == "__main__":
    main()
