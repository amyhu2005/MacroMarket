"""
Shared paper-scope filter for the three viz exports (opportunity scatter,
geo network, co-occurrence network).

Scope, per request:
    - Macro, Econometrics papers: full inclusion.
    - Applied papers: narrowed to "applied econometrics regarding macro" only
      - a paper must (a) use an econometric identification method per
      method_trends.METHOD_PATTERNS (title+abstract keyword match) and
      (b) touch a Macro topic via a secondary/tertiary topic tag (its primary
      topic is Applied, but the paper is also substantively about a macro
      subject). This is much narrower than "all of Applied."
    - Micro: excluded entirely.

Usage:
    from scope_filter import get_scoped_paper_ids, SCOPE_LEVEL1
    ids = get_scoped_paper_ids()
"""
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from topic_taxonomy import TOPIC_TAXONOMY
from topic_taxonomy_secondary import SECONDARY_TOPIC_TAXONOMY, DEFAULT_BUCKET
from method_trends import METHOD_PATTERNS

ROOT = Path(__file__).resolve().parent.parent
PROC_DIR = ROOT / "data" / "processed"

SCOPE_LEVEL1 = {"Macro", "Econometrics", "Applied"}
CORE_LEVEL1 = {"Macro", "Econometrics"}

_METHOD_RX = re.compile("|".join(p for _, p in METHOD_PATTERNS), re.IGNORECASE)


def _classify(topic):
    if topic in TOPIC_TAXONOMY:
        return TOPIC_TAXONOMY[topic]
    if topic in SECONDARY_TOPIC_TAXONOMY:
        return SECONDARY_TOPIC_TAXONOMY[topic]
    return DEFAULT_BUCKET


def get_scoped_paper_ids(papers=None, topics_long=None):
    """Paper IDs in scope: all Macro/Econometrics papers, plus Applied papers
    that are both econometrically-identified and macro-touching."""
    if papers is None:
        papers = pd.read_csv(PROC_DIR / "papers.csv")
    if topics_long is None:
        topics_long = pd.read_csv(PROC_DIR / "topics_long.csv")

    core_ids = set(papers.loc[papers.level1.isin(CORE_LEVEL1), "paper_id"])

    applied = papers[papers.level1 == "Applied"]
    text = (applied["title"].fillna("") + " " + applied["abstract"].fillna("")).str.lower()
    has_method = text.str.contains(_METHOD_RX, regex=True, na=False)
    applied_method_ids = set(applied.loc[has_method, "paper_id"])

    tl = topics_long.copy()
    tl["level1"] = tl["topic"].map(lambda t: _classify(t)[0])
    touches_macro_ids = set(tl.loc[tl.level1 == "Macro", "paper_id"])

    applied_scoped_ids = applied_method_ids & touches_macro_ids

    return core_ids | applied_scoped_ids


if __name__ == "__main__":
    ids = get_scoped_paper_ids()
    papers = pd.read_csv(PROC_DIR / "papers.csv")
    scoped = papers[papers.paper_id.isin(ids)]
    print(f"Scoped papers: {len(ids)}")
    print(scoped.level1.value_counts())
