"""
Saturation analysis: for each topic, paper volume vs. citation impact.

Uses OpenAlex's field-weighted citation impact (fwci, mean=1.0 across the
comparison set) and citation_percentile instead of raw cited_by_count, since
raw counts are heavily biased toward older papers (a 2022 paper has had ~3
more years to accumulate citations than a 2025 paper) - fwci and percentile
are already normalized for publication age and field.

Quadrant logic (relative to median volume / median fwci across level2 topics):
    high volume + high fwci  -> "hot & rewarded"   (crowded, but citations follow)
    low volume  + high fwci  -> "underexplored"    (gap worth entering)
    high volume + low fwci   -> "oversaturated"    (crowded, diminishing returns)
    low volume  + low fwci   -> "quiet"            (low activity, low payoff so far)

Usage:
    python scripts/citation_saturation.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROC_DIR = ROOT / "data" / "processed"

MIN_TOTAL_PAPERS = 8


def main():
    papers = pd.read_csv(PROC_DIR / "papers.csv")
    papers = papers.dropna(subset=["level1", "fwci"])

    agg = (
        papers.groupby(["level1", "level2"])
        .agg(
            paper_count=("paper_id", "count"),
            mean_fwci=("fwci", "mean"),
            median_fwci=("fwci", "median"),
            mean_citation_percentile=("citation_percentile", "mean"),
            pct_top10=("is_top10pct_cited", "mean"),
        )
        .reset_index()
    )
    agg = agg[agg.paper_count >= MIN_TOTAL_PAPERS].round(3)
    agg["pct_top10"] = (agg["pct_top10"] * 100).round(1)

    vol_median = agg["paper_count"].median()
    fwci_median = agg["median_fwci"].median()

    def quadrant(row):
        hi_vol = row.paper_count >= vol_median
        hi_impact = row.median_fwci >= fwci_median
        if hi_vol and hi_impact:
            return "hot_and_rewarded"
        if not hi_vol and hi_impact:
            return "underexplored_gap"
        if hi_vol and not hi_impact:
            return "oversaturated"
        return "quiet"

    agg["quadrant"] = agg.apply(quadrant, axis=1)
    agg = agg.sort_values("median_fwci", ascending=False)
    agg.to_csv(PROC_DIR / "topic_saturation_level2.csv", index=False)

    print(f"(volume median={vol_median}, fwci median={fwci_median})\n")
    for q in ["underexplored_gap", "hot_and_rewarded", "oversaturated", "quiet"]:
        sub = agg[agg.quadrant == q].sort_values("median_fwci", ascending=False)
        print(f"=== {q} ({len(sub)} topics) ===")
        print(sub[["level1", "level2", "paper_count", "mean_fwci", "median_fwci", "pct_top10"]].to_string(index=False))
        print()


if __name__ == "__main__":
    main()
