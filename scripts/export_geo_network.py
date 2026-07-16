"""
Export compact JSON for the geographic collaboration network: institutions
(sized by paper count, positioned by lat/lon), authors (for zoom-in decluster),
and co-authorship edges - restricted to Macro/Econometrics papers plus Applied
papers narrowed to "applied econometrics regarding macro" (see scope_filter.py).

Uses compact integer indices instead of full OpenAlex URLs to keep payload small.

Usage:
    python scripts/export_geo_network.py
"""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scope_filter import get_scoped_paper_ids
from institution_corrections import INSTITUTION_ID_MERGES, INSTITUTIONS_EXCLUDED_FROM_GEO

ROOT = Path(__file__).resolve().parent.parent
PROC_DIR = ROOT / "data" / "processed"


def main():
    papers = pd.read_csv(PROC_DIR / "papers.csv")
    authorships = pd.read_csv(PROC_DIR / "authorships.csv")
    with open(PROC_DIR / "institution_geo_cache.json") as f:
        geo_cache = json.load(f)

    # geo_cache is keyed by raw OpenAlex institution_id, fetched straight from
    # the API - it never saw institution_corrections.py's name fixes, and the
    # mis-linked IDs point at a real, differently-located place (e.g.
    # "Moscow Institute of Thermal Technology" really is in Moscow). Merge
    # authorships on those wrong IDs onto their correctly-linked counterpart
    # before any aggregation, and drop the one with no valid counterpart.
    authorships = authorships[~authorships.institution_id.isin(INSTITUTIONS_EXCLUDED_FROM_GEO)].copy()
    authorships["institution_id"] = authorships["institution_id"].replace(INSTITUTION_ID_MERGES)

    scoped_ids = get_scoped_paper_ids(papers)
    scope_papers = papers[papers.paper_id.isin(scoped_ids)]
    scope_paper_ids = set(scope_papers["paper_id"])
    level1_by_paper = dict(zip(scope_papers.paper_id, scope_papers.level1))

    auth = authorships[authorships.paper_id.isin(scope_paper_ids)].dropna(subset=["author_id"]).copy()

    # keep only institutions with valid geo coords
    def has_geo(inst_id):
        g = geo_cache.get(inst_id)
        return g is not None and g.get("lat") is not None

    auth_geo = auth[auth.institution_id.notna() & auth.institution_id.map(has_geo)]

    # one primary institution per author = the one they appear with most often in scope
    author_inst = (
        auth_geo.groupby(["author_id", "institution_id"]).size().reset_index(name="n")
        .sort_values("n", ascending=False)
        .drop_duplicates("author_id", keep="first")
    )
    author_name = auth.drop_duplicates("author_id").set_index("author_id")["author_name"].to_dict()

    # dominant level1 per author (across their in-scope papers)
    auth["level1"] = auth["paper_id"].map(level1_by_paper)
    author_level1 = (
        auth.groupby(["author_id", "level1"]).size().reset_index(name="n")
        .sort_values("n", ascending=False).drop_duplicates("author_id", keep="first")
        .set_index("author_id")["level1"].to_dict()
    )
    author_paper_count = auth.groupby("author_id")["paper_id"].nunique().to_dict()

    # institutions actually used (appear as somebody's primary institution)
    used_inst_ids = sorted(author_inst["institution_id"].unique())
    inst_index = {iid: i for i, iid in enumerate(used_inst_ids)}

    institutions = []
    for iid in used_inst_ids:
        g = geo_cache[iid]
        inst_papers = auth_geo[auth_geo.institution_id == iid]["paper_id"].unique()
        inst_papers_df = scope_papers[scope_papers.paper_id.isin(inst_papers)]
        inst_level1_counts = inst_papers_df["level1"].value_counts()
        dominant = inst_level1_counts.idxmax() if len(inst_level1_counts) else "Applied"

        topic_counts = (
            inst_papers_df.groupby(["level1", "level2"]).size()
            .reset_index(name="n").sort_values("n", ascending=False)
        )
        topics = [
            {"level1": r.level1, "level2": r.level2, "n": int(r.n)}
            for r in topic_counts.itertuples()
        ]

        institutions.append({
            "name": g["name"],
            "lat": round(g["lat"], 3),
            "lon": round(g["lon"], 3),
            "paperCount": int(len(inst_papers)),
            "level1": dominant,
            "topics": topics,
        })

    author_to_inst = dict(zip(author_inst.author_id, author_inst.institution_id))
    used_author_ids = sorted(author_to_inst.keys())
    author_index = {aid: i for i, aid in enumerate(used_author_ids)}

    authors = []
    for aid in used_author_ids:
        authors.append({
            "name": author_name.get(aid, "Unknown"),
            "inst": inst_index[author_to_inst[aid]],
            "papers": int(author_paper_count.get(aid, 0)),
            "level1": author_level1.get(aid, "Applied"),
        })

    # co-authorship edges among used authors, weighted by shared in-scope papers, colored by dominant level1
    pair_data = {}
    for pid, g in auth[auth.author_id.isin(used_author_ids)].groupby("paper_id"):
        ids = [a for a in g.author_id.unique() if a in author_index]
        lvl1 = level1_by_paper.get(pid, "Applied")
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                key = tuple(sorted([author_index[ids[i]], author_index[ids[j]]]))
                d = pair_data.setdefault(key, {"weight": 0, "level1_counts": {}})
                d["weight"] += 1
                d["level1_counts"][lvl1] = d["level1_counts"].get(lvl1, 0) + 1

    edges = []
    for (a, b), d in pair_data.items():
        dominant = max(d["level1_counts"], key=d["level1_counts"].get)
        edges.append({"a": a, "b": b, "w": d["weight"], "level1": dominant})

    out = {"institutions": institutions, "authors": authors, "edges": edges}
    out_path = PROC_DIR / "viz_geo_network.json"
    with open(out_path, "w") as f:
        json.dump(out, f, separators=(",", ":"))

    print(f"institutions: {len(institutions)}, authors: {len(authors)}, edges: {len(edges)}")
    print(f"Wrote {out_path} ({out_path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
