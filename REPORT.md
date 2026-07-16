# Economics Journal Trends Report (2022–2025)

*AER, Econometrica, JPE, QJE, ReStud — topics, schools, and where the research frontier is moving*

---

## Executive Summary

1,830 articles published 2022–2025 across the top-5 economics journals were collected, classified into a Macro/Micro/Econometrics/Applied taxonomy, and analyzed for topic trends, institutional specialization, citation impact, method adoption, topic combinations, and collaboration structure.

**Top three candidate research directions** (full reasoning in [§12](#12-final-recommendations-candidate-research-directions)):

1. **International monetary policy transmission**, using modern causal-identification methods (event studies, DiD) rather than classical VAR — sits at the intersection of an under-published-but-well-cited macro subject and a fast-rising topic combination.
2. **Climate/energy shocks and business cycles** — a citation-rewarded, low-volume macro subject whose pairing with environmental economics is one of the fastest-rising (small-base) combinations in the dataset.
3. **Structurally-disciplined machine learning** (ML as an estimation tool inside a structural model, not as the paper's main contribution) — ML is the fastest-growing method tag but hasn't yet earned citation traction on its own in these five journals, while structural/DSGE work has an established track record.

---

## 1. Data Collection

**Methodology.** Papers were pulled from the [OpenAlex](https://openalex.org) API rather than scraped directly from journal websites, since OpenAlex indexes journal metadata for free and several of these journals are paywalled (scraping them directly would likely violate ToS). For each journal's OpenAlex source ID, all works were paginated via cursor pagination with `filter=primary_location.source.id:{id},publication_year:2022|2023|2024|2025,type:article` (the `type:article` filter excludes front matter, corrections, and editorial content). Raw JSON pages were cached locally (`data/raw/`) so the pipeline is re-runnable without re-hitting the API. Script: `scripts/fetch_openalex.py`.

**Fields captured per paper:** title, abstract (reconstructed from OpenAlex's inverted-index representation), DOI, journal, publication date/year, citation count, field-weighted citation impact (fwci), citation percentile, and OpenAlex's topic classification (primary + secondary + tertiary topics, each with a topic → subfield → field → domain hierarchy). Per author: name, ORCID, author position, and institutional affiliation(s) (name, country, type). Script: `scripts/build_dataset.py`.

**Volume:**

| Journal | Papers |
|---|---|
| JPE | 442 |
| AER | 422 |
| ReStud | 397 |
| Econometrica | 382 |
| QJE | 187 |
| **Total** | **1,830** |

| Year | Papers |
|---|---|
| 2022 | 428 |
| 2023 | 464 |
| 2024 | 469 |
| 2025 | 469 |

5,962 (author × institution) affiliation records were extracted across 3,189 distinct authors.

---

## 2. Data Quality: Institution Mis-Linking

**Methodology.** Before trusting any institution-based ranking, the top ~250 institutions by raw paper count were spot-checked by cross-referencing the author names attached to each institution against known real-world affiliations.

**Finding.** OpenAlex's automated affiliation-string matching has systematic acronym/name-collision errors. Confirmed cases in the top 100 institutions by volume:

| OpenAlex mis-linked to | Actually meant | Evidence |
|---|---|---|
| Moscow Institute of Thermal Technology | Massachusetts Institute of Technology ("MIT") | Authors Iván Werning, Abhijit Banerjee, Benjamin Olken, Michael Whinston — all MIT faculty |
| International Zinc Association ("IZA") | IZA – Institute of Labor Economics | Authors are labor economists (job search, unemployment) publishing in a Bonn-based labor research network |
| Bread for the World Institute | BREAD (Bureau for Research and Economic Analysis of Development) | Authors are development economists (Imbert, Martínez-Bravo, Padró i Miquel, Sviatschi) |
| John Brown University (small Arkansas college) | Brown University | 34 of 36 "Brown"-affiliated authorships were mis-linked (94% error rate) — authors include Peter Hull, John N. Friedman, Jonathan Roth |
| Harvard University Press | Harvard University | 52 of 122 "Harvard"-affiliated authorships mis-linked (43%) — authors include Raj Chetty, Oliver Hart, Emmanuel Farhi |
| Berkeley College (small NY/NJ for-profit college) | University of California, Berkeley | Authors David Card, Stefano DellaVigna, Reed Walker |
| California University of Pennsylvania | University of Pennsylvania | Authors Gilles Duranton, Harold L. Cole, Guillermo Ordoñez |
| Kellogg's (Canada) (the cereal company) | Northwestern University (Kellogg School of Management) | Authors Nancy Qian, Nicola Persico |

All eight are corrected in `scripts/institution_corrections.py` and applied during `build_dataset.py`. **Limitation:** institutions below ~12 papers were not individually audited; similar noise likely exists in the long tail but won't move any top-N ranking materially.

---

## 3. Topic Taxonomy

**Methodology.** OpenAlex assigns each paper a `primary_topic` from its own fine-grained taxonomy (269 distinct values appeared in this dataset). There is no free, reliably-attached JEL-code source for these journals, so a 3-level taxonomy was hand-built by classifying all 269 topics against JEL-inspired categories:

- **Level 1**: Macro / Micro / Econometrics / Applied
- **Level 2**: a subcategory within Level 1 (e.g., under Macro: Monetary Policy & Central Banking, Business Cycles & Growth, Fiscal Policy, Financial Markets & Stability)
- **Level 3**: OpenAlex's original topic label

This mapping is a judgment call, not an official classification — it lives in `scripts/topic_taxonomy.py` and is fully editable. 2 of 1,830 papers had no primary topic and are excluded from taxonomy-dependent analyses.

**Level 1 breakdown:**

| Level 1 | Papers | Share |
|---|---|---|
| Applied | 988 | 54.0% |
| Micro | 424 | 23.2% |
| Macro | 328 | 17.9% |
| Econometrics | 88 | 4.8% |

**Top 10 Level 2 subjects overall:**

| Level 1 | Level 2 | Papers |
|---|---|---|
| Applied | Labor Economics | 181 |
| Macro | Financial Markets & Stability | 151 |
| Applied | Other / Interdisciplinary | 134 |
| Applied | Political Economy & Governance | 120 |
| Applied | Development Economics | 112 |
| Micro | General Economic Theory | 103 |
| Micro | Industrial Organization & Competition | 98 |
| Applied | Corporate & Household Finance | 88 |
| Micro | Auctions & Market Design | 80 |
| Macro | Fiscal Policy | 78 |

Note Econometrics is small (4.8%) as a *primary*-topic category — most econometrically-focused papers get tagged by OpenAlex under their subject-matter topic instead (e.g. a causal-inference labor paper is tagged "Labor market dynamics," not "Causal Inference"). This is why §8 (method mining) searches abstract text directly rather than relying on this tag alone.

---

## 4. Topic Rankings by Institution ("Schools Ranked by Topic")

**Methodology.** For each (paper, institution) pair — deduplicated so an institution is credited at most once per paper regardless of how many of its authors are on that paper ("whole counting," not fractional) — institutions were ranked by paper count within each Level 2 subject. Script: `scripts/analyze.py` → `institutions_by_topic.csv`.

**Top 20 institutions overall (all subjects):**

| Institution | Papers |
|---|---|
| National Bureau of Economic Research | 185 |
| University of Chicago | 145 |
| Center for Economic and Policy Research | 142 |
| University of California, Berkeley | 116 |
| Stanford University | 92 |
| Harvard University | 89 |
| Yale University | 88 |
| Princeton University | 80 |
| Columbia University | 66 |
| Massachusetts Institute of Technology | 63 |
| Centre for Economic Policy Research (London) | 58 |
| New York University | 56 |
| Northwestern University | 50 |
| University of Pennsylvania | 49 |
| LSE | 46 |
| Duke University | 42 |
| University College London | 39 |
| University of Oxford | 39 |
| University of Toronto | 38 |
| Boston University | 38 |

**Note:** NBER, CEPR (both the DC think tank and the London research network), and IZA are research *networks*, not degree-granting universities — economists list them as secondary affiliations alongside their home institution, which is why they rank so highly. If you want a "universities only" view, this is a quick filter I can add.

**Sample subject leaderboards (macro/econometrics-relevant):**

*Macro / Monetary Policy & Central Banking:* NBER (11), CEPR-DC (7), U Chicago (7), Princeton (6), UC Berkeley (6)

*Macro / Business Cycles & Growth:* CEPR-DC (7), NBER (5), NYU (4), LSE (3), UCL (3)

*Applied / International Trade:* CEPR-DC (12), Yale (9), NBER (6), Harvard (4), Princeton (4)

*Econometrics / Causal Inference & Identification:* Brown (3), Harvard (3), Columbia (2), Stanford (2), UCL (2) — small-n, noisy (only 26 papers total in this bucket)

*Econometrics / Machine Learning in Economics:* NBER (2), Northwestern (2), Princeton (2) — extremely small-n (19 papers total), essentially a three-way tie

*Applied / Labor Economics:* NBER (23), CEPR-DC (18), U Chicago (15), UC Berkeley (14), IZA (10)

*Applied / Development Economics:* CEPR-DC (15), NBER (11), UC Berkeley (9), U Chicago (9), Harvard (7)

---

## 5. Institution Topic Profiles ("Topics Ranked by School")

**Methodology.** Inverse of §4 — for each institution with ≥3 papers, its own papers are ranked by Level 2 subject to show specialization. Script: `scripts/analyze.py` → `topics_by_institution.csv`.

| Institution | Total papers | Top 3 specializations |
|---|---|---|
| NBER | 185 | Financial Markets & Stability (26), Labor Economics (23), Health Economics (14) |
| University of Chicago | 145 | Labor Economics (15), Education Economics (12), Health Economics (11) |
| MIT | 63 | Labor Economics (8), Health Economics (6), Industrial Organization & Competition (6) |
| UC Berkeley | 116 | Labor Economics (14), Financial Markets & Stability (10), Corporate & Household Finance (9) |
| Harvard | 89 | Political Economy & Governance (9), Behavioral & Experimental Economics (8), Development Economics (7) |

Labor Economics dominates nearly every major institution's output — consistent with it being the single largest Level 2 subject overall (§3).

---

## 6. Topic Momentum (Growth Analysis)

**Methodology.** Raw volume tells you what's *big*, not what's *moving*. Each Level 2/3 subject's paper count in an early window (2022–2023) is compared to a late window (2024–2025) using a symmetric growth rate — `(late − early) / (mean of early, late) × 100` — which is robust to a zero-early-count case and bounded to ±200%, unlike a naive percent-change formula. Subjects with fewer than 8 total papers across the 4 years are excluded as too noisy to trust. Script: `scripts/topic_momentum.py`.

**Level 2 momentum, full ranking:**

| Level 1 | Level 2 | 2022–23 | 2024–25 | Total | Growth |
|---|---|---|---|---|---|
| Econometrics | Machine Learning in Economics | 5 | 14 | 19 | **+94.7%** |
| Econometrics | Time Series & Panel Data Methods | 3 | 6 | 9 | +66.7% |
| Econometrics | Statistical & Bayesian Methods | 12 | 22 | 34 | +58.8% |
| Applied | Political Economy & Governance | 43 | 77 | 120 | +56.7% |
| Applied | Other / Interdisciplinary | 53 | 81 | 134 | +41.8% |
| Applied | Health Economics | 31 | 45 | 76 | +36.8% |
| Applied | International Trade | 27 | 38 | 65 | +33.8% |
| Applied | Urban & Regional Economics | 16 | 22 | 38 | +31.6% |
| Micro | Game Theory & Mechanism Design | 28 | 37 | 65 | +27.7% |
| Applied | Environmental & Energy Economics | 26 | 33 | 59 | +23.7% |
| Applied | Labor Economics | 80 | 101 | 181 | +23.2% |
| Micro | Industrial Organization & Competition | 47 | 51 | 98 | +8.2% |
| Macro | Financial Markets & Stability | 73 | 78 | 151 | +6.6% |
| Macro | Business Cycles & Growth | 18 | 19 | 37 | +5.4% |
| Applied | Education Economics | 35 | 35 | 70 | 0.0% |
| Applied | Development Economics | 60 | 52 | 112 | −14.3% |
| Macro | Monetary Policy & Central Banking | 34 | 28 | 62 | −19.4% |
| Applied | Economic History | 10 | 8 | 18 | −22.2% |
| Macro | Fiscal Policy | 44 | 34 | 78 | −25.6% |
| Applied | Corporate & Household Finance | 50 | 38 | 88 | −27.3% |
| Econometrics | Causal Inference & Identification | 15 | 11 | 26 | −30.8% |
| Micro | Behavioral & Experimental Economics | 46 | 32 | 78 | −35.9% |
| Applied | Public Finance & Taxation | 17 | 10 | 27 | −51.9% |
| Micro | Auctions & Market Design | 52 | 28 | 80 | **−60.0%** |
| Micro | General Economic Theory | 67 | 36 | 103 | **−60.2%** |

**Reading this for macro/econometrics:** within Macro, only Financial Markets & Stability and Business Cycles & Growth are growing (slowly); Monetary Policy and Fiscal Policy are both declining in share. Within Econometrics, all three subcategories are growing — ML fastest by far, though off a small base (§8 has the more precise method-level view).

---

## 7. Citation-Weighted Saturation Analysis

**Methodology.** Raw citation counts are biased toward older papers — a 2022 paper has had ~3 more years to accumulate citations than a 2025 paper. OpenAlex's **field-weighted citation impact (fwci)** already corrects for this (and for field norms; fwci = 1.0 is the field average), so it's used instead of raw `cited_by_count`. For each Level 2 subject (min. 8 papers), median fwci is plotted against paper volume, and each subject is bucketed into a quadrant relative to the median volume (70 papers) and median fwci (6.28) across all subjects:

- **Underexplored gap**: below-median volume, above-median impact → citations reward the (few) papers that do get written here
- **Hot & rewarded**: above-median volume, above-median impact → crowded but the crowding is justified
- **Oversaturated**: above-median volume, below-median impact → crowded with diminishing returns
- **Quiet**: below-median volume, below-median impact → low activity, no strong payoff signal yet

Script: `scripts/citation_saturation.py`.

| Quadrant | Level 1 | Level 2 | Papers | Median fwci |
|---|---|---|---|---|
| **Underexplored gap** | Applied | Urban & Regional Economics | 38 | 17.0 |
| Underexplored gap | Econometrics | Time Series & Panel Data Methods | 9 | 12.8 |
| **Underexplored gap** | **Macro** | **Business Cycles & Growth** | 37 | 10.1 |
| **Underexplored gap** | **Macro** | **Monetary Policy & Central Banking** | 62 | 8.6 |
| Underexplored gap | Applied | Economic History | 18 | 8.3 |
| Underexplored gap | Applied | International Trade | 64 | 8.0 |
| Underexplored gap | Applied | Public Finance & Taxation | 27 | 7.3 |
| Hot & rewarded | Applied | Education Economics | 70 | 12.4 |
| Hot & rewarded | Applied | Labor Economics | 181 | 11.2 |
| Hot & rewarded | Applied | Development Economics | 112 | 10.9 |
| Hot & rewarded | Applied | Political Economy & Governance | 120 | 8.8 |
| Hot & rewarded | Applied | Health Economics | 76 | 6.7 |
| Hot & rewarded | Macro | Financial Markets & Stability | 151 | 6.3 |
| Oversaturated | Micro | Industrial Organization & Competition | 98 | 5.7 |
| Oversaturated | Applied | Corporate & Household Finance | 88 | 5.3 |
| Oversaturated | Macro | Fiscal Policy | 78 | 5.0 |
| Oversaturated | Micro | General Economic Theory | 103 | 4.3 |
| Oversaturated | Micro | Behavioral & Experimental Economics | 78 | 4.3 |
| Oversaturated | Micro | Auctions & Market Design | 80 | 2.4 |
| Oversaturated | Applied | Other / Interdisciplinary | 134 | 0.0 |
| Quiet | Applied | Environmental & Energy Economics | 59 | 6.0 |
| **Quiet** | **Econometrics** | **Causal Inference & Identification** | 26 | 4.1 |
| Quiet | Econometrics | Statistical & Bayesian Methods | 34 | 3.8 |
| **Quiet** | **Econometrics** | **Machine Learning in Economics** | 19 | 2.9 |
| Quiet | Micro | Game Theory & Mechanism Design | 65 | 2.4 |

**Key signal for your focus:** Monetary Policy & Central Banking and Business Cycles & Growth — the two core macro subjects — are both citation-rewarded gaps: not many papers, but the ones that get published do well. Causal Inference and Machine Learning (Econometrics) are "quiet" — activity is picking up (§6) but citation payoff hasn't followed yet, meaning either it's early (opportunity) or the bar for landing these methods well in a top-5 journal is still high (risk). Worth noting Causal Inference's *mean* fwci (29.2) is far above its *median* (4.1) — a few blockbuster papers are pulling the mean up while most papers in that bucket get modest citations; the distribution is highly skewed, not uniformly rewarding.

---

## 8. Method-Trend Mining

**Methodology.** OpenAlex's topic tags describe subject matter, not econometric technique, so a fastest-growing *method* signal required searching title+abstract text directly for technique-indicating phrases (regex, case-insensitive, phrase-based to avoid bare-acronym false positives like "IV" or "DID"). **Scoped to Macro + Econometrics + Applied papers only** (1,404 of 1,830), excluding Micro, per request — the goal is empirical/identification strategy trends in macro-adjacent work, not pure theory. Script: `scripts/method_trends.py`.

| Method | 2022 | 2023 | 2024 | 2025 | Total | Growth | % of scope |
|---|---|---|---|---|---|---|---|
| Structural Estimation / DSGE | 11 | 25 | 18 | 15 | 69 | −8.7% | 4.9% |
| RCT / Field Experiment | 14 | 10 | 22 | 15 | 61 | +42.6% | 4.3% |
| Instrumental Variables | 9 | 4 | 5 | 10 | 28 | +14.3% | 2.0% |
| Natural / Quasi-Experiment | 9 | 6 | 7 | 6 | 28 | −14.3% | 2.0% |
| Difference-in-Differences | 7 | 5 | 7 | 8 | 27 | +22.2% | 1.9% |
| Panel Data / Fixed Effects | 4 | 7 | 12 | 4 | 27 | +37.0% | 1.9% |
| Regression Discontinuity | 9 | 1 | 5 | 5 | 20 | 0.0% | 1.4% |
| Event Study | 0 | 5 | 6 | 4 | 15 | +66.7% | 1.1% |
| Machine Learning / Text-as-Data | 2 | 1 | 3 | 6 | 12 | **+100.0%** | 0.9% |
| Time Series (VAR/Local Proj.) | 1 | 4 | 1 | 1 | 7 | −85.7% | 0.5% |
| Bayesian Methods | 2 | 1 | 0 | 0 | 3 | −200.0% | 0.2% |
| Synthetic Control | 1 | 2 | 0 | 0 | 3 | −200.0% | 0.2% |

**Reading this:** Structural/DSGE modeling is still the largest declared empirical approach in macro-adjacent work by a wide margin, though flat-to-slightly-declining. RCTs/field experiments and event studies are both growing meaningfully. Classical time-series methods (VAR/local projections) are shrinking fast, though off a tiny base — worth treating as a weak signal. ML/text-as-data has the highest growth rate of any method but is still under 1% of papers — consistent with §7's finding that ML hasn't yet built a strong citation track record here.

---

## 9. Topic Co-occurrence / White-Space Analysis

**Methodology.** Uses OpenAlex's secondary and tertiary topic assignments (not just primary), which add 219 additional distinct topic labels beyond the 269 primary ones. Topics occurring ≥5 times in a secondary/tertiary slot were individually classified into the taxonomy (`scripts/topic_taxonomy_secondary.py`); the long tail below that (mostly singleton, often off-subject noise from OpenAlex's classifier) falls back to a default "Applied / Other" bucket rather than being hand-audited one by one. For each paper, all distinct Level 2 tags it touches (across primary+secondary+tertiary) are paired up, and pairs with ≥4 co-occurring papers are kept, then compared early (2022–23) vs late (2024–25) window like §6. Script: `scripts/topic_cooccurrence.py`.

**Most common combinations overall** (top 5): Macro/Financial Markets & Stability × Micro/General Economic Theory (90 papers, declining −40%); Applied/Other × Applied/Political Economy & Governance (84, +28.6%); Macro/Financial Markets & Stability × Macro/Monetary Policy (74, −37.8%); Applied/Corporate & Household Finance × Macro/Financial Markets & Stability (72, −16.7%); Macro/Monetary Policy × Micro/General Economic Theory (69, −31.9%).

**Rare-but-rising combinations touching Macro or Econometrics** (4–10 total papers, sorted by growth):

| Combination | Total | 2022–23 | 2024–25 | Growth |
|---|---|---|---|---|
| Applied/Health Economics × Econometrics/Statistical & Bayesian Methods | 5 | 1 | 4 | +120.0% |
| Macro/Financial Markets & Stability × Micro/Industrial Organization | 9 | 2 | 7 | +111.1% |
| Econometrics/Statistical & Bayesian Methods × Micro/Auctions & Market Design | 4 | 1 | 3 | +100.0% |
| Econometrics/Statistical & Bayesian Methods × Econometrics/Time Series | 4 | 1 | 3 | +100.0% |
| Applied/Economic History × Macro/Monetary Policy & Central Banking | 4 | 1 | 3 | +100.0% |
| Applied/Other × Econometrics/Causal Inference & Identification | 7 | 2 | 5 | +85.7% |
| **Applied/International Trade × Macro/Financial Markets & Stability** | 10 | 3 | 7 | **+80.0%** |
| **Applied/International Trade × Macro/Monetary Policy & Central Banking** | 9 | 3 | 6 | **+66.7%** |
| Econometrics/Machine Learning × Econometrics/Statistical & Bayesian Methods | 6 | 2 | 4 | +66.7% |
| Applied/Environmental & Energy Economics × Macro/Business Cycles & Growth | 8 | 3 | 5 | +50.0% |

**This is the section most directly behind recommendations #1 and #2** in §12: International Trade pairing with both Financial Markets & Stability and Monetary Policy is rising fast, and Environmental & Energy Economics pairing with Business Cycles & Growth is rising fast — both off small bases, meaning early but real.

---

## 10. Collaboration Network Analysis

**Methodology.** A co-authorship graph was built (networkx) with one node per author (3,189 nodes) and an edge between any two authors who share a paper, weighted by number of shared papers (5,532 edges). From this graph: (a) approximate betweenness centrality (`k=500` sample, seed=42) identifies authors who structurally bridge otherwise-separate parts of the co-authorship network; (b) greedy modularity community detection (`networkx.algorithms.community.greedy_modularity_communities`) partitions the graph into data-driven "schools" — clusters of frequently-co-publishing authors, not ideological schools of thought; (c) separately, each author's own papers are cross-referenced against the Level 2 taxonomy to compute a topic-diversity score (how many distinct subjects their papers span), which is a different notion of "bridging" — spanning subject areas rather than spanning the social graph. Script: `scripts/collaboration_network.py`.

**Collaboration trends by year:**

| Year | Avg. authors/paper | % multi-institution | % international |
|---|---|---|---|
| 2022 | 2.21 | 63.3% | 38.1% |
| 2023 | 2.49 | 68.5% | 37.9% |
| 2024 | 2.41 | 70.1% | 43.1% |
| 2025 | 2.38 | 64.8% | 38.0% |

No strong monotonic trend — collaboration intensity is roughly flat with year-to-year noise, not a clear rise.

**Top collaborator pairs (most shared papers, 2022–2025):** Mira Frick × Ryota Iijima (5); Michela Carlana × Eliana La Ferrara (4); Olivier Coibion × Yuriy Gorodnichenko (4); Ryota Iijima × Yuhta Ishii (4); Kei Kawai × Jun Nakabayashi (4).

**724 collaboration communities detected.** The 10 largest (size 54–86 authors) each have a recognizable institutional and topical signature — e.g. community #0 (86 authors) centers on NBER/CEPR/Stanford and Financial Markets & Stability + Labor; community #8 (63 authors) centers on NBER/Harvard/MIT and is overwhelmingly Health Economics (47 of its papers).

**Bridge authors (betweenness — structurally connect the co-authorship graph):** Guido Lorenzoni, George-Marios Angeletos, and Iván Werning form a tightly-connected macro-theory cluster (community #5) with the highest betweenness scores in the dataset. A second cluster (community #17: Virgiliu Midrigan, Olivier Wang, Thomas Philippon, Daniel Yi Xu, Juan Carlos Suárez Serrato) bridges macro-finance and firm-level topics.

**Bridge authors (topic diversity — span the most distinct subjects, ≥2 papers):** Philipp Strack (7 distinct Level 2 subjects across 8 papers, spanning Auctions/Game Theory through Financial Markets and Health); Daron Acemoğlu (7 subjects across 9 papers); Magne Mogstad (6 subjects across 6 papers); **Victor Chernozhukov** (4 subjects across 5 papers: Health Economics, Causal Inference & Identification, Statistical & Bayesian Methods, **Monetary Policy & Central Banking**) — notably the one author in the top-diversity list whose span directly connects rigorous econometric identification to a core macro subject.

---

## 11. Known Limitations

- **Taxonomy is a judgment call.** The Level 1/2 mapping (§3) is hand-built without an official JEL-code source; review `scripts/topic_taxonomy.py` if any classification looks wrong to you.
- **Institution corrections cover only the top ~100 by volume** (§2); lower-count institutions weren't individually audited.
- **Whole counting, not fractional**, for institution credit — a 5-author paper with 3 Stanford authors still only credits Stanford once, but a paper with 1 Stanford + 1 MIT author credits both fully (no double-counting discount).
- **Method mining is keyword-based**, not a semantic classifier — it will miss papers that use a technique without using its standard name, and can't distinguish "we use DiD" from "prior work uses DiD, we do something else."
- **Small-n cells throughout are noisy** — anything under ~10 papers (many Econometrics-tagged subjects, most co-occurrence pairs) should be read as a directional hint, not a precise estimate.
- **fwci/citation percentile** still partially reward older papers within the same year cohort (more time even within a year), though far less than raw citation counts.

---

## 12. Final Recommendations: Candidate Research Directions

### 1. International monetary policy transmission via modern causal identification
**Why:** Monetary Policy & Central Banking is a citation-rewarded gap (§7: 62 papers, median fwci 8.6, above the 6.28 median) — not oversaturated, but not ignored either. Its co-occurrence with International Trade is one of the fastest-rising small-base combinations in the dataset (§9: +66.7%, and Financial Markets × Trade at +80.0%). Meanwhile, Event Study and DiD are both growing methods in macro-adjacent work (§8: +66.7% and +22.2% respectively) while classical VAR/local-projections approaches are shrinking (−85.7%, small base). **Together**: a paper studying cross-border monetary policy spillovers or transmission using an event-study/DiD design around identifiable policy shocks sits at the intersection of an underexplored, well-cited subject and a rising, currently-underused-in-this-niche method.
**Starting point:** Victor Chernozhukov's recent work (§10) is the one author in the dataset who already bridges rigorous causal inference and monetary policy — a natural literature-review anchor.

### 2. Climate/energy shocks and business cycles
**Why:** Business Cycles & Growth is also a citation-rewarded gap (§7: median fwci 10.1, second-highest of all macro subjects). Its pairing with Environmental & Energy Economics is rising fast off a small base (§9: +50.0%, 8 total papers) — early enough that the space isn't crowded, but the trend line is real, not a one-off.
**Starting point:** Pull the 8 papers behind that co-occurrence pair (`topic_cooccurrence_pairs.csv`) as a direct reading list — this is a small enough set to read in full.

### 3. Structurally-disciplined machine learning (ML as a tool, not the headline)
**Why:** ML/text-as-data is the fastest-growing method tag in macro-adjacent work by far (§8: +100.0%) and Machine Learning in Economics is the fastest-growing Level 2 subject overall (§6: +94.7%) — but both are still under 1–2% of papers, and §7 shows Machine Learning in Economics sitting in the "quiet" citation quadrant (median fwci 2.9, below the 6.28 median). Structural/DSGE work, by contrast, is the single largest declared method (69 papers) with a much stronger citation history. The gap between "ML is growing fast" and "ML hasn't earned citations yet" suggests the more promising move is using ML as an estimation component *inside* a structurally-motivated model, rather than positioning the paper as an ML paper.
**Risk to weigh:** this could also mean top-5 reviewers are simply slower to reward ML-forward papers regardless of framing — worth reading a few of the 19 Machine Learning in Economics papers directly to gauge how they were received before committing to this angle.

---

## 13. File Reference

All outputs live in `data/processed/`:

| File | Section | Contents |
|---|---|---|
| `papers.csv` | §1, §3 | One row per paper: metadata, citations, taxonomy tags |
| `authorships.csv` | §1, §2 | One row per (paper, author, institution) |
| `topic_taxonomy.csv` | §3 | Editable topic → Level1/Level2 mapping |
| `topic_rankings_level2.csv` / `_level3.csv` | §3 | Subject rankings by volume |
| `institutions_by_topic.csv` | §4 | Per subject, institutions ranked by paper count |
| `institution_rankings.csv` | §4 | Institutions ranked by total papers |
| `topics_by_institution.csv` | §5 | Per institution, subject specialization |
| `topic_momentum_level2.csv` / `_level3.csv` | §6 | Growth rates, early vs. late window |
| `topic_saturation_level2.csv` | §7 | Volume vs. fwci, quadrant-classified |
| `method_trends_summary.csv` / `_by_year.csv` | §8 | Keyword-mined method trends |
| `topic_cooccurrence_pairs.csv` | §9 | Topic-pair co-occurrence and growth |
| `collaboration_trends_by_year.csv` | §10 | Avg. authors, multi-institution %, international % |
| `top_collaborator_pairs.csv` | §10 | Most frequent co-author pairs |
| `author_network_stats.csv` | §10 | Per-author degree, betweenness, topic diversity |
| `collaboration_communities.csv` | §10 | Data-driven collaboration clusters |
