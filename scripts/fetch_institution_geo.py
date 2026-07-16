"""
Fetch lat/lon (and city/country) for every institution that appears in the
Macro/Econometrics/Applied scope, via OpenAlex's /institutions endpoint.
Caches raw responses so it's resumable.

Usage:
    python scripts/fetch_institution_geo.py
"""
import json
import time
from pathlib import Path

import pandas as pd
import requests

MAILTO = "strt.fkng.writing@gmail.com"
ROOT = Path(__file__).resolve().parent.parent
PROC_DIR = ROOT / "data" / "processed"
CACHE_PATH = PROC_DIR / "institution_geo_cache.json"

SCOPE_LEVEL1 = {"Macro", "Econometrics", "Applied"}


def main():
    papers = pd.read_csv(PROC_DIR / "papers.csv")
    authorships = pd.read_csv(PROC_DIR / "authorships.csv")

    scope_paper_ids = set(papers[papers.level1.isin(SCOPE_LEVEL1)]["paper_id"])
    scope_auth = authorships[authorships.paper_id.isin(scope_paper_ids)]
    inst_ids = sorted(scope_auth["institution_id"].dropna().unique())
    print(f"{len(inst_ids)} distinct institutions to fetch")

    cache = {}
    if CACHE_PATH.exists():
        with open(CACHE_PATH) as f:
            cache = json.load(f)
        print(f"resuming, {len(cache)} already cached")

    for i, inst_id in enumerate(inst_ids):
        short_id = inst_id.rsplit("/", 1)[-1]
        if inst_id in cache:
            continue
        url = f"https://api.openalex.org/institutions/{short_id}"
        try:
            resp = requests.get(url, params={"mailto": MAILTO}, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            geo = data.get("geo") or {}
            cache[inst_id] = {
                "name": data.get("display_name"),
                "lat": geo.get("latitude"),
                "lon": geo.get("longitude"),
                "city": geo.get("city"),
                "country": geo.get("country"),
            }
        except Exception as e:
            print(f"  FAILED {inst_id}: {e}")
            cache[inst_id] = {"name": None, "lat": None, "lon": None, "city": None, "country": None}

        if (i + 1) % 50 == 0:
            print(f"  {i+1}/{len(inst_ids)} fetched")
            with open(CACHE_PATH, "w") as f:
                json.dump(cache, f)
        time.sleep(0.05)

    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f)

    n_with_geo = sum(1 for v in cache.values() if v.get("lat") is not None)
    print(f"Done. {n_with_geo}/{len(cache)} institutions have geo coordinates")


if __name__ == "__main__":
    main()
