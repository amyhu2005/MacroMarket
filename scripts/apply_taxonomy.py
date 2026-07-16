"""
Apply the hand-built topic taxonomy (scripts/topic_taxonomy.py) to papers.csv,
adding level1/level2/level3 tag columns. Also writes an editable
data/processed/topic_taxonomy.csv for review.

Usage:
    python scripts/apply_taxonomy.py
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from topic_taxonomy import TOPIC_TAXONOMY

ROOT = Path(__file__).resolve().parent.parent
PROC_DIR = ROOT / "data" / "processed"


def main():
    papers = pd.read_csv(PROC_DIR / "papers.csv")
    distinct_topics = pd.read_csv(PROC_DIR / "distinct_topics.csv")

    # validate full coverage
    missing = set(distinct_topics["topic"].dropna()) - set(TOPIC_TAXONOMY.keys())
    if missing:
        raise SystemExit(f"{len(missing)} topics missing from taxonomy: {sorted(missing)}")

    extra = set(TOPIC_TAXONOMY.keys()) - set(distinct_topics["topic"].dropna())
    if extra:
        print(f"NOTE: {len(extra)} taxonomy entries don't match any distinct topic (stale?): {sorted(extra)}")

    # write editable taxonomy csv for review
    tax_rows = [
        {"topic": t, "level1": v[0], "level2": v[1]}
        for t, v in TOPIC_TAXONOMY.items()
    ]
    tax_df = pd.DataFrame(tax_rows).sort_values(["level1", "level2", "topic"])
    tax_df.to_csv(PROC_DIR / "topic_taxonomy.csv", index=False)

    # apply to papers
    papers["level1"] = papers["primary_topic"].map(lambda t: TOPIC_TAXONOMY.get(t, (None, None))[0])
    papers["level2"] = papers["primary_topic"].map(lambda t: TOPIC_TAXONOMY.get(t, (None, None))[1])
    papers["level3"] = papers["primary_topic"]

    papers.to_csv(PROC_DIR / "papers.csv", index=False)

    print(f"Tagged {len(papers)} papers.")
    print(f"\nLevel 1 breakdown:\n{papers['level1'].value_counts()}")
    print(f"\nUnclassified (no primary_topic): {papers['level1'].isna().sum()}")
    print(f"\nTop Level 2 within Macro:\n{papers[papers.level1=='Macro']['level2'].value_counts()}")
    print(f"\nTop Level 2 within Applied:\n{papers[papers.level1=='Applied']['level2'].value_counts().head(10)}")


if __name__ == "__main__":
    main()
