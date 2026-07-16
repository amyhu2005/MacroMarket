"""
Parse cached OpenAlex raw JSON pages into normalized tables:
    data/processed/papers.csv        - one row per paper
    data/processed/authorships.csv   - one row per (paper, author, institution)
    data/processed/distinct_topics.csv - one row per distinct primary_topic seen,
                                          for manual classification into a taxonomy

Usage:
    python scripts/build_dataset.py
"""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from institution_corrections import INSTITUTION_CORRECTIONS

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
OUT_DIR = ROOT / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def reconstruct_abstract(inverted_index):
    if not inverted_index:
        return ""
    positions = {}
    for word, idxs in inverted_index.items():
        for i in idxs:
            positions[i] = word
    return " ".join(positions[i] for i in sorted(positions))


def load_all_works():
    works = []
    for path in sorted(RAW_DIR.glob("*.json")):
        with open(path) as f:
            data = json.load(f)
        journal = path.stem.rsplit("_", 1)[0]
        for w in data["results"]:
            w["_journal"] = journal
            works.append(w)
    return works


def main():
    works = load_all_works()
    print(f"Loaded {len(works)} raw works")

    paper_rows = []
    authorship_rows = []
    topic_long_rows = []
    topic_counter = {}
    all_topic_counter = {}  # includes secondary/tertiary topics, for coverage checking

    for w in works:
        paper_id = w["id"]
        primary_topic = w.get("primary_topic") or {}
        subfield = primary_topic.get("subfield") or {}
        field = primary_topic.get("field") or {}
        domain = primary_topic.get("domain") or {}
        cnp = w.get("citation_normalized_percentile") or {}

        paper_rows.append({
            "paper_id": paper_id,
            "doi": w.get("doi"),
            "title": w.get("title"),
            "abstract": reconstruct_abstract(w.get("abstract_inverted_index")),
            "journal": w["_journal"],
            "year": w.get("publication_year"),
            "date": w.get("publication_date"),
            "cited_by_count": w.get("cited_by_count"),
            "fwci": w.get("fwci"),
            "citation_percentile": cnp.get("value"),
            "is_top1pct_cited": cnp.get("is_in_top_1_percent"),
            "is_top10pct_cited": cnp.get("is_in_top_10_percent"),
            "primary_topic": primary_topic.get("display_name"),
            "primary_topic_id": primary_topic.get("id"),
            "subfield": subfield.get("display_name"),
            "field": field.get("display_name"),
            "domain": domain.get("display_name"),
            "n_authors": len(w.get("authorships") or []),
            "n_institutions": w.get("institutions_distinct_count"),
            "n_countries": w.get("countries_distinct_count"),
        })

        if primary_topic.get("display_name"):
            key = (primary_topic["display_name"], subfield.get("display_name"),
                   field.get("display_name"), domain.get("display_name"))
            topic_counter[key] = topic_counter.get(key, 0) + 1

        for rank, t in enumerate(w.get("topics") or [], start=1):
            topic_long_rows.append({
                "paper_id": paper_id,
                "rank": rank,
                "topic": t.get("display_name"),
                "score": t.get("score"),
                "subfield": (t.get("subfield") or {}).get("display_name"),
                "field": (t.get("field") or {}).get("display_name"),
                "domain": (t.get("domain") or {}).get("display_name"),
            })
            all_topic_counter[t.get("display_name")] = all_topic_counter.get(t.get("display_name"), 0) + 1

        for a in w.get("authorships") or []:
            author = a.get("author") or {}
            institutions = a.get("institutions") or [{}]
            for inst in institutions:
                inst_id = inst.get("id")
                inst_name = INSTITUTION_CORRECTIONS.get(inst_id, inst.get("display_name"))
                authorship_rows.append({
                    "paper_id": paper_id,
                    "author_id": author.get("id"),
                    "author_name": author.get("display_name"),
                    "author_position": a.get("author_position"),
                    "is_corresponding": a.get("is_corresponding"),
                    "institution_id": inst_id,
                    "institution_name": inst_name,
                    "institution_type": inst.get("type"),
                    "institution_country": inst.get("country_code"),
                })

    papers = pd.DataFrame(paper_rows)
    authorships = pd.DataFrame(authorship_rows)

    topics_rows = [
        {"topic": k[0], "subfield": k[1], "field": k[2], "domain": k[3], "paper_count": v}
        for k, v in topic_counter.items()
    ]
    distinct_topics = pd.DataFrame(topics_rows).sort_values("paper_count", ascending=False)
    topics_long = pd.DataFrame(topic_long_rows)

    papers.to_csv(OUT_DIR / "papers.csv", index=False)
    authorships.to_csv(OUT_DIR / "authorships.csv", index=False)
    distinct_topics.to_csv(OUT_DIR / "distinct_topics.csv", index=False)
    topics_long.to_csv(OUT_DIR / "topics_long.csv", index=False)

    all_distinct = pd.DataFrame(
        [{"topic": k, "occurrences": v} for k, v in all_topic_counter.items()]
    ).sort_values("occurrences", ascending=False)
    all_distinct.to_csv(OUT_DIR / "distinct_topics_all_ranks.csv", index=False)

    print(f"papers.csv: {len(papers)} rows")
    print(f"authorships.csv: {len(authorships)} rows")
    print(f"distinct_topics.csv: {len(distinct_topics)} distinct primary topics")
    print(f"topics_long.csv: {len(topics_long)} rows (primary+secondary+tertiary topics per paper)")
    print(f"distinct_topics_all_ranks.csv: {len(all_distinct)} distinct topics across all ranks")
    print(f"\nJournal breakdown:\n{papers['journal'].value_counts()}")
    print(f"\nYear breakdown:\n{papers['year'].value_counts().sort_index()}")
    print(f"\nMissing primary_topic: {papers['primary_topic'].isna().sum()}")
    print(f"Papers with no institution on any author: "
          f"{authorships.groupby('paper_id')['institution_id'].apply(lambda s: s.isna().all()).sum()}")


if __name__ == "__main__":
    main()
