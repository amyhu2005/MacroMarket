"""
Export compact JSON for the topic co-occurrence network, restricted to
Macro/Econometrics papers plus Applied papers narrowed to "applied
econometrics regarding macro" (see scope_filter.py): both the paper pool AND
the topic tags themselves must be in scope (a Macro paper's Micro-tagged
secondary topic is dropped, not just Micro-primary papers).

Usage:
    python scripts/export_cooccurrence_network.py
"""
import json
import sys
from itertools import combinations
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from topic_taxonomy import TOPIC_TAXONOMY
from topic_taxonomy_secondary import SECONDARY_TOPIC_TAXONOMY, DEFAULT_BUCKET
from scope_filter import get_scoped_paper_ids, SCOPE_LEVEL1

ROOT = Path(__file__).resolve().parent.parent
PROC_DIR = ROOT / "data" / "processed"

MIN_PAIR_PAPERS = 3


def classify(topic):
    if topic in TOPIC_TAXONOMY:
        return TOPIC_TAXONOMY[topic]
    if topic in SECONDARY_TOPIC_TAXONOMY:
        return SECONDARY_TOPIC_TAXONOMY[topic]
    return DEFAULT_BUCKET


def main():
    topics_long = pd.read_csv(PROC_DIR / "topics_long.csv")
    papers = pd.read_csv(PROC_DIR / "papers.csv")[["paper_id", "year", "level1"]]

    scoped_ids = get_scoped_paper_ids()
    scope_papers = papers[papers.paper_id.isin(scoped_ids)]
    topics_long = topics_long.merge(scope_papers[["paper_id", "year"]], on="paper_id")

    topics_long["level1"], topics_long["level2"] = zip(*topics_long["topic"].map(classify))
    topics_long = topics_long[topics_long.level1.isin(SCOPE_LEVEL1)]
    topics_long["tag"] = topics_long["level1"] + " / " + topics_long["level2"]

    paper_tags = topics_long[["paper_id", "tag", "level1", "year"]].drop_duplicates(subset=["paper_id", "tag"])

    # node volumes (count of in-scope papers touching this level2, at any rank)
    node_volume = paper_tags.groupby(["tag", "level1"])["paper_id"].nunique().reset_index(name="volume")

    pair_counter = {}
    for paper_id, g in paper_tags.groupby("paper_id"):
        tags = sorted(g["tag"].unique())
        year = g["year"].iloc[0]
        for a, b in combinations(tags, 2):
            key = (a, b)
            pair_counter.setdefault(key, {"total": 0, "early": 0, "late": 0})
            pair_counter[key]["total"] += 1
            if year in (2022, 2023):
                pair_counter[key]["early"] += 1
            else:
                pair_counter[key]["late"] += 1

    nodes = [
        {"id": r.tag, "level1": r.level1, "label": r.tag.split(" / ", 1)[1], "volume": int(r.volume)}
        for r in node_volume.itertuples()
    ]

    edges = []
    for (a, b), v in pair_counter.items():
        if v["total"] < MIN_PAIR_PAPERS:
            continue
        growth = (
            (v["late"] - v["early"]) / ((v["early"] + v["late"]) / 2) * 100
            if (v["early"] + v["late"]) > 0 else 0
        )
        edges.append({"source": a, "target": b, "weight": v["total"], "growth_pct": round(growth, 1)})

    out = {"nodes": nodes, "edges": edges}
    out_path = PROC_DIR / "viz_cooccurrence_network.json"
    with open(out_path, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    print(f"Wrote {out_path}: {len(nodes)} nodes, {len(edges)} edges, {out_path.stat().st_size} bytes")


if __name__ == "__main__":
    main()
