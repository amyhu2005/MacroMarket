# MacroMarket — Economics Journal Trends

Analyzes papers published 2022–2025 in the top-5 economics journals (AER,
Econometrica, JPE, QJE, ReStud) via the OpenAlex API: topics, institutions
("schools"), and rankings. Visualization layer to come later.

## Pipeline

```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python scripts/fetch_openalex.py      # caches raw JSON -> data/raw/
python scripts/build_dataset.py       # -> data/processed/papers.csv, authorships.csv, distinct_topics.csv
python scripts/apply_taxonomy.py      # tags papers with level1/level2/level3 -> data/processed/topic_taxonomy.csv
python scripts/analyze.py             # rankings -> data/processed/*.csv
```

## Data model

- **papers.csv** — one row per paper: title, abstract, journal, year, citation count,
  and taxonomy tags (`level1`, `level2`, `level3`).
- **authorships.csv** — one row per (paper, author, institution): author name/ORCID,
  position, and institutional affiliation ("school").
- **Taxonomy** (`scripts/topic_taxonomy.py`): every paper's OpenAlex `primary_topic`
  (269 distinct values in this dataset) is hand-mapped to:
  - `level1`: Macro / Micro / Econometrics / Applied
  - `level2`: a JEL-inspired subcategory (e.g. Monetary Policy & Central Banking,
    Labor Economics, Causal Inference & Identification)
  - `level3`: the original OpenAlex topic label
  This is an interpretive mapping (no free official JEL-code source is cleanly
  attached to these journals) — review/edit `scripts/topic_taxonomy.py` directly.

## Known data quality issue: institution mis-linking

OpenAlex's automated affiliation-string matching has acronym/name collisions —
e.g. author affiliation "MIT" was linked to *Moscow Institute of Thermal
Technology* instead of *Massachusetts Institute of Technology*; "IZA" to
*International Zinc Association* instead of the *IZA Institute of Labor
Economics*; "Brown University" mostly linked to *John Brown University* (a small
Arkansas college); similar issues for Harvard, Penn, Berkeley, and Northwestern's
Kellogg School. These were found by spot-checking the top 100 institutions by
paper count against known author affiliations and are corrected in
`scripts/institution_corrections.py`, applied during `build_dataset.py`.
Lower-count institutions (< ~12 papers) were not individually audited — similar
noise may exist there but won't move top-N rankings.

## Rankings output (`data/processed/`)

- `topic_rankings_level2.csv` / `topic_rankings_level3.csv` — most-published-about subjects
- `topic_trend_level1_by_year.csv` / `topic_trend_level2_by_year.csv` — trends over 2022–2025
- `institutions_by_topic.csv` — per subject, institutions ranked by paper count
- `institution_rankings.csv` — institutions ranked by total paper count
- `topics_by_institution.csv` — per institution (≥3 papers), subjects ranked by paper count

Institution credit uses whole counting: an institution is credited once per
paper if any of its authors is affiliated with it (not fractional).

## Deeper analyses (`scripts/`, outputs in `data/processed/`)

- `topic_momentum.py` — early (2022-23) vs late (2024-25) growth rate per subject,
  not just raw volume -> `topic_momentum_level2.csv` / `_level3.csv`
- `citation_saturation.py` — volume vs. field-weighted citation impact (fwci) per
  subject, quadrant-classified (underexplored gap / hot & rewarded / oversaturated
  / quiet) -> `topic_saturation_level2.csv`
- `method_trends.py` — keyword-mined empirical/econometric technique trends
  (DiD, RDD, IV, event study, structural/DSGE, ML, Bayesian, etc.), scoped to
  Macro + Econometrics + Applied papers only -> `method_trends_summary.csv`,
  `method_trends_by_year.csv`
- `topic_cooccurrence.py` — which subject *combinations* appear together on the
  same paper (via primary+secondary+tertiary OpenAlex topics), and which
  combinations are rare-but-rising -> `topic_cooccurrence_pairs.csv`
- `collaboration_network.py` — co-authorship graph: collaboration trends by
  year, top collaborator pairs, betweenness-based "bridge" authors, topic-diversity
  bridge authors, and data-driven collaboration communities ("schools") via
  modularity clustering -> `collaboration_trends_by_year.csv`,
  `top_collaborator_pairs.csv`, `author_network_stats.csv`,
  `collaboration_communities.csv`

Run in this order after the core pipeline: `topic_momentum.py`,
`citation_saturation.py`, `method_trends.py`, `topic_cooccurrence.py`,
`collaboration_network.py` (each only depends on `data/processed/papers.csv` /
`authorships.csv` / `topics_long.csv`, all independent of each other).
