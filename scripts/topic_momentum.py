"""
Momentum ranking: which subjects are growing fastest, not just biggest.

For each level2 (and level3) topic, compares early window (2022-2023) vs late
window (2024-2025) paper counts. Uses a minimum volume threshold to avoid
noisy percentage swings from tiny denominators.

Usage:
    python scripts/topic_momentum.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROC_DIR = ROOT / "data" / "processed"

MIN_TOTAL_PAPERS = 8  # exclude topics too small to compute a meaningful growth rate


def momentum_table(papers: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    papers = papers.copy()
    papers["window"] = papers["year"].map(lambda y: "early_2022_23" if y in (2022, 2023) else "late_2024_25")

    counts = (
        papers.groupby(group_cols + ["window"]).size()
        .unstack("window", fill_value=0)
        .reset_index()
    )
    counts["total"] = counts["early_2022_23"] + counts["late_2024_25"]
    counts = counts[counts["total"] >= MIN_TOTAL_PAPERS].copy()

    # symmetric growth rate: (late - early) / ((early + late)/2), robust to early=0
    counts["growth_rate_pct"] = (
        (counts["late_2024_25"] - counts["early_2022_23"])
        / ((counts["early_2022_23"] + counts["late_2024_25"]) / 2)
        * 100
    ).round(1)

    return counts.sort_values("growth_rate_pct", ascending=False)


def main():
    papers = pd.read_csv(PROC_DIR / "papers.csv")
    papers = papers.dropna(subset=["level1"])

    l2 = momentum_table(papers, ["level1", "level2"])
    l2.to_csv(PROC_DIR / "topic_momentum_level2.csv", index=False)

    l3 = momentum_table(papers, ["level1", "level2", "level3"])
    l3.to_csv(PROC_DIR / "topic_momentum_level3.csv", index=False)

    print(f"=== Level 2 momentum (min {MIN_TOTAL_PAPERS} papers, sorted by growth) ===")
    print(l2[["level1", "level2", "early_2022_23", "late_2024_25", "total", "growth_rate_pct"]].to_string(index=False))

    print(f"\n=== Level 3 (fine-grained) momentum, top 15 gainers ===")
    print(l3[["level1", "level2", "level3", "early_2022_23", "late_2024_25", "total", "growth_rate_pct"]].head(15).to_string(index=False))

    print(f"\n=== Level 3 (fine-grained) momentum, top 15 decliners ===")
    print(l3[["level1", "level2", "level3", "early_2022_23", "late_2024_25", "total", "growth_rate_pct"]].tail(15).to_string(index=False))


if __name__ == "__main__":
    main()
