"""
Topic co-occurrence / white-space analysis: which level2 subject *combinations*
show up together on the same paper (via OpenAlex's primary+secondary+tertiary
topics), and which combinations are rare-but-rising vs already crowded.

Note: topics with occurrence >= 5 among secondary/tertiary-only topics are
individually classified (topic_taxonomy_secondary.py); everything below that
falls back to a default bucket (Applied / Other-Interdisciplinary) - precision
matters less in the long tail for a co-occurrence signal.

Usage:
    python scripts/topic_cooccurrence.py
"""
import sys
from itertools import combinations
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from topic_taxonomy import TOPIC_TAXONOMY
from topic_taxonomy_secondary import SECONDARY_TOPIC_TAXONOMY, DEFAULT_BUCKET

ROOT = Path(__file__).resolve().parent.parent
PROC_DIR = ROOT / "data" / "processed"

MIN_PAIR_PAPERS = 4
FOCUS_LEVEL1 = {"Macro", "Econometrics", "Applied"}


def classify(topic):
    if topic in TOPIC_TAXONOMY:
        return TOPIC_TAXONOMY[topic]
    if topic in SECONDARY_TOPIC_TAXONOMY:
        return SECONDARY_TOPIC_TAXONOMY[topic]
    return DEFAULT_BUCKET


def main():
    topics_long = pd.read_csv(PROC_DIR / "topics_long.csv")
    papers = pd.read_csv(PROC_DIR / "papers.csv")[["paper_id", "year"]]

    topics_long["level1"], topics_long["level2"] = zip(*topics_long["topic"].map(classify))
    topics_long["tag"] = topics_long["level1"] + " / " + topics_long["level2"]

    # one row per (paper, distinct level2 tag) - a paper can hit the same
    # level2 bucket via multiple ranks, dedupe those
    paper_tags = topics_long[["paper_id", "tag"]].drop_duplicates()
    paper_tags = paper_tags.merge(papers, on="paper_id")

    grouped = paper_tags.groupby("paper_id")
    pair_counter = {}
    for paper_id, g in grouped:
        tags = sorted(g["tag"].unique())
        year = papers.loc[papers.paper_id == paper_id, "year"].iloc[0]
        for a, b in combinations(tags, 2):
            key = (a, b)
            pair_counter.setdefault(key, {"total": 0, "early": 0, "late": 0})
            pair_counter[key]["total"] += 1
            if year in (2022, 2023):
                pair_counter[key]["early"] += 1
            else:
                pair_counter[key]["late"] += 1

    rows = [
        {"tag_a": k[0], "tag_b": k[1], "total": v["total"], "early_2022_23": v["early"], "late_2024_25": v["late"]}
        for k, v in pair_counter.items()
    ]
    pairs = pd.DataFrame(rows)
    pairs = pairs[pairs.total >= MIN_PAIR_PAPERS].copy()
    pairs["growth_rate_pct"] = (
        (pairs["late_2024_25"] - pairs["early_2022_23"])
        / ((pairs["early_2022_23"] + pairs["late_2024_25"]) / 2)
        * 100
    ).round(1)
    pairs = pairs.sort_values("total", ascending=False)
    pairs.to_csv(PROC_DIR / "topic_cooccurrence_pairs.csv", index=False)

    # focus: pairs where at least one side is Macro or Econometrics
    focus = pairs[
        pairs.tag_a.str.startswith(("Macro", "Econometrics"))
        | pairs.tag_b.str.startswith(("Macro", "Econometrics"))
    ].copy()

    print(f"{len(pairs)} distinct topic-pairs with >= {MIN_PAIR_PAPERS} co-occurring papers\n")
    print("=== Most common combinations overall ===")
    print(pairs.head(15).to_string(index=False))

    print("\n=== Combinations involving Macro or Econometrics, by volume ===")
    print(focus.sort_values("total", ascending=False).head(15).to_string(index=False))

    print("\n=== Rare-but-rising combinations (Macro/Econometrics side, total 4-10, sorted by growth) ===")
    rising = focus[(focus.total >= MIN_PAIR_PAPERS) & (focus.total <= 10)].sort_values("growth_rate_pct", ascending=False)
    print(rising.head(15).to_string(index=False))


if __name__ == "__main__":
    main()
