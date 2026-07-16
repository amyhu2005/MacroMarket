"""
Compute rankings from the tagged dataset:
    - most-published-about subjects overall and by year (trend)
    - per subject: institutions ranked by # papers in that subject
    - per institution: subjects ranked by # papers (specialization profile)

Institution credit uses "whole counting": an institution gets credit for a
paper if any of its authors is affiliated with it (no fractional splitting
across co-authors/institutions).

Usage:
    python scripts/analyze.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROC_DIR = ROOT / "data" / "processed"

MIN_INSTITUTION_PAPERS = 3  # filter noise out of institution rankings


def main():
    papers = pd.read_csv(PROC_DIR / "papers.csv")
    authorships = pd.read_csv(PROC_DIR / "authorships.csv")

    papers = papers.dropna(subset=["level1"])

    # one row per (paper, institution) - whole counting
    paper_inst = authorships.dropna(subset=["institution_id"])[
        ["paper_id", "institution_id", "institution_name", "institution_country"]
    ].drop_duplicates()

    paper_inst_topic = paper_inst.merge(
        papers[["paper_id", "journal", "year", "level1", "level2", "level3", "cited_by_count"]],
        on="paper_id", how="inner",
    )

    # 1. Most talked-about subjects overall
    topic_rankings_l2 = (
        papers.groupby(["level1", "level2"]).size()
        .reset_index(name="paper_count")
        .sort_values("paper_count", ascending=False)
    )
    topic_rankings_l2.to_csv(PROC_DIR / "topic_rankings_level2.csv", index=False)

    topic_rankings_l3 = (
        papers.groupby(["level1", "level2", "level3"]).size()
        .reset_index(name="paper_count")
        .sort_values("paper_count", ascending=False)
    )
    topic_rankings_l3.to_csv(PROC_DIR / "topic_rankings_level3.csv", index=False)

    # 2. Trend over time (by year) for level1 and level2
    trend_l1 = (
        papers.groupby(["year", "level1"]).size()
        .reset_index(name="paper_count")
        .sort_values(["level1", "year"])
    )
    trend_l1.to_csv(PROC_DIR / "topic_trend_level1_by_year.csv", index=False)

    trend_l2 = (
        papers.groupby(["year", "level1", "level2"]).size()
        .reset_index(name="paper_count")
        .sort_values(["level1", "level2", "year"])
    )
    trend_l2.to_csv(PROC_DIR / "topic_trend_level2_by_year.csv", index=False)

    # 3. Per subject (level2): institutions ranked by # papers in that subject
    inst_by_topic = (
        paper_inst_topic.groupby(["level1", "level2", "institution_name"])["paper_id"]
        .nunique()
        .reset_index(name="paper_count")
        .sort_values(["level1", "level2", "paper_count"], ascending=[True, True, False])
    )
    inst_by_topic.to_csv(PROC_DIR / "institutions_by_topic.csv", index=False)

    # 4. Per institution: overall paper counts + topic specialization profile
    institution_totals = (
        paper_inst_topic.groupby("institution_name")["paper_id"]
        .nunique()
        .reset_index(name="total_papers")
        .sort_values("total_papers", ascending=False)
    )
    institution_totals.to_csv(PROC_DIR / "institution_rankings.csv", index=False)

    topics_by_institution = (
        paper_inst_topic.groupby(["institution_name", "level1", "level2"])["paper_id"]
        .nunique()
        .reset_index(name="paper_count")
        .sort_values(["institution_name", "paper_count"], ascending=[True, False])
    )
    # only keep institutions with enough volume to be meaningful
    qualifying = institution_totals[institution_totals.total_papers >= MIN_INSTITUTION_PAPERS]["institution_name"]
    topics_by_institution = topics_by_institution[topics_by_institution.institution_name.isin(qualifying)]
    topics_by_institution.to_csv(PROC_DIR / "topics_by_institution.csv", index=False)

    # --- console summary ---
    print("=== Level 1 breakdown ===")
    print(papers["level1"].value_counts())

    print("\n=== Top 15 subjects overall (level2) ===")
    print(topic_rankings_l2.head(15).to_string(index=False))

    print("\n=== Top 20 institutions overall (by paper count, whole-counted) ===")
    print(institution_totals.head(20).to_string(index=False))

    print("\n=== Top 5 institutions in Macro / Monetary Policy & Central Banking ===")
    sub = inst_by_topic[(inst_by_topic.level1 == "Macro") & (inst_by_topic.level2 == "Monetary Policy & Central Banking")]
    print(sub.head(5).to_string(index=False))

    print("\n=== Top 5 institutions in Econometrics / Causal Inference & Identification ===")
    sub = inst_by_topic[(inst_by_topic.level1 == "Econometrics") & (inst_by_topic.level2 == "Causal Inference & Identification")]
    print(sub.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
