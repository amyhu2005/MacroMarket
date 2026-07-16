"""
Export compact JSON for the opportunity scatter (§7 saturation analysis as a
chart): every Level 2 subject as a bubble, x=volume, y=fwci, size=growth rate,
color=Level 1. Scoped to Macro/Econometrics papers plus Applied papers that
are narrowed to "applied econometrics regarding macro" (see scope_filter.py).

Usage:
    python scripts/export_opportunity_scatter.py
"""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scope_filter import get_scoped_paper_ids
from topic_momentum import momentum_table

ROOT = Path(__file__).resolve().parent.parent
PROC_DIR = ROOT / "data" / "processed"

MIN_TOTAL_PAPERS = 8


def main():
    all_papers = pd.read_csv(PROC_DIR / "papers.csv")
    scoped_ids = get_scoped_paper_ids(all_papers)
    scoped_papers = all_papers[all_papers.paper_id.isin(scoped_ids)]
    papers = scoped_papers[scoped_papers.fwci.notna()]

    agg = (
        papers.groupby(["level1", "level2"])
        .agg(volume=("paper_id", "count"), mean_fwci=("fwci", "mean"), median_fwci=("fwci", "median"))
        .reset_index()
    )
    agg = agg[agg.volume >= MIN_TOTAL_PAPERS]

    # recomputed on the scoped (narrowed-Applied) paper set, not the full
    # Applied dataset, so growth rates stay consistent with the bubble volumes
    momentum = momentum_table(scoped_papers, ["level1", "level2"])[["level1", "level2", "growth_rate_pct"]]

    merged = agg.merge(momentum, on=["level1", "level2"], how="left")
    merged["growth_rate_pct"] = merged["growth_rate_pct"].fillna(0)

    vol_med = merged["volume"].median()
    fwci_med = merged["median_fwci"].median()

    def quadrant(row):
        hi_vol = row.volume >= vol_med
        hi_impact = row.median_fwci >= fwci_med
        if hi_vol and hi_impact:
            return "hot_and_rewarded"
        if not hi_vol and hi_impact:
            return "underexplored_gap"
        if hi_vol and not hi_impact:
            return "oversaturated"
        return "quiet"

    merged["quadrant"] = merged.apply(quadrant, axis=1)

    out = {
        "vol_median": round(float(vol_med), 1),
        "fwci_median": round(float(fwci_med), 2),
        "topics": [
            {
                "level1": r.level1,
                "level2": r.level2,
                "volume": int(r.volume),
                "mean_fwci": round(float(r.mean_fwci), 2),
                "median_fwci": round(float(r.median_fwci), 2),
                "growth_pct": round(float(r.growth_rate_pct), 1),
                "quadrant": r.quadrant,
            }
            for r in merged.itertuples()
        ],
    }

    out_path = PROC_DIR / "viz_opportunity_scatter.json"
    with open(out_path, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    print(f"Wrote {out_path} ({len(out['topics'])} topics, {out_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
