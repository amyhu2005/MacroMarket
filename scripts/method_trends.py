"""
Method-trend mining: which econometric/empirical techniques are gaining
ground, based on keyword search over title+abstract.

Scoped to Macro + Econometrics + Applied papers only (excludes Micro), per
request - the interest is in identification/estimation strategy trends within
macro-adjacent empirical work, not pure theory.

Usage:
    python scripts/method_trends.py
"""
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROC_DIR = ROOT / "data" / "processed"

# (method label, regex pattern) - patterns use word boundaries / phrases to
# avoid false positives from common-word collisions (e.g. bare "IV", "DID").
METHOD_PATTERNS = [
    ("Difference-in-Differences", r"difference[\s-]in[\s-]differences?|diff-in-diff|triple difference|\bDDD\b"),
    ("Regression Discontinuity", r"regression discontinuit|\bRDD\b|\bRD design\b"),
    ("Instrumental Variables", r"instrumental variables?|\b2SLS\b|two-stage least squares|IV estimat|IV strateg"),
    ("Event Study", r"event[\s-]stud(?:y|ies)"),
    ("Synthetic Control", r"synthetic control"),
    ("RCT / Field Experiment", r"randomi[sz]ed controlled trial|randomi[sz]ed experiment|field experiment|\bRCT\b"),
    ("Natural / Quasi-Experiment", r"natural experiment|quasi-experimental"),
    ("Structural Estimation / DSGE", r"structural model|structural estimation|\bDSGE\b|general equilibrium model|heterogeneous.agent|\bHANK\b"),
    ("Time Series (VAR/Local Proj.)", r"vector autoregression|\bVAR model\b|local projections?|\bSVAR\b|structural VAR"),
    ("Machine Learning / Text-as-Data", r"machine learning|deep learning|neural network|random forest|\bLASSO\b|text as data|natural language processing|large language model"),
    ("Bayesian Methods", r"Bayesian estimation|Bayesian model|\bMCMC\b|Markov chain Monte Carlo"),
    ("Panel Data / Fixed Effects", r"panel data|fixed[\s-]effects? (?:model|estimat|regression|specification)"),
]

SCOPE_LEVEL1 = {"Macro", "Econometrics", "Applied"}


def main():
    papers = pd.read_csv(PROC_DIR / "papers.csv")
    papers = papers[papers.level1.isin(SCOPE_LEVEL1)].copy()
    papers["text"] = (papers["title"].fillna("") + " " + papers["abstract"].fillna("")).str.lower()

    rows = []
    for label, pattern in METHOD_PATTERNS:
        rx = re.compile(pattern, re.IGNORECASE)
        hit = papers["text"].str.contains(rx, regex=True, na=False)
        papers[f"method__{label}"] = hit
        for year, sub in papers[hit].groupby("year"):
            rows.append({"method": label, "year": year, "paper_count": len(sub)})

    method_by_year = pd.DataFrame(rows)
    method_by_year.to_csv(PROC_DIR / "method_trends_by_year.csv", index=False)

    totals = (
        method_by_year.groupby("method")["paper_count"].sum()
        .reset_index(name="total_papers")
        .sort_values("total_papers", ascending=False)
    )

    piv = method_by_year.pivot(index="method", columns="year", values="paper_count").fillna(0)
    piv["total"] = piv.sum(axis=1)
    early_cols = [c for c in piv.columns if c in (2022, 2023)]
    late_cols = [c for c in piv.columns if c in (2024, 2025)]
    piv["early_2022_23"] = piv[early_cols].sum(axis=1)
    piv["late_2024_25"] = piv[late_cols].sum(axis=1)
    piv["growth_rate_pct"] = (
        (piv["late_2024_25"] - piv["early_2022_23"])
        / ((piv["early_2022_23"] + piv["late_2024_25"]) / 2).replace(0, pd.NA)
        * 100
    ).round(1)
    piv = piv.sort_values("total", ascending=False)
    piv.to_csv(PROC_DIR / "method_trends_summary.csv")

    n_scope = len(papers)
    print(f"Scope: {n_scope} papers (Macro + Econometrics + Applied)\n")
    print("=== Method prevalence & momentum (2022-23 vs 2024-25) ===")
    print(piv[[2022, 2023, 2024, 2025, "total", "growth_rate_pct"]].to_string())

    print("\n=== Share of scoped papers mentioning each method ===")
    totals["pct_of_scope"] = (totals["total_papers"] / n_scope * 100).round(1)
    print(totals.to_string(index=False))


if __name__ == "__main__":
    main()
