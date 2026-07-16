"""
Collaboration structure:
    - trends: avg authors/paper, % multi-institution, % international, by year
    - co-authorship graph: who collaborates with whom, weighted by shared papers
    - community detection ("schools" as data-driven collaboration clusters)
    - bridge authors/institutions: those whose papers span multiple level2 topics,
      i.e. who connect otherwise-separate research areas

Usage:
    python scripts/collaboration_network.py
"""
from pathlib import Path

import networkx as nx
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROC_DIR = ROOT / "data" / "processed"

MIN_PAPERS_FOR_BRIDGE_STATS = 2


def build_trends(papers: pd.DataFrame):
    trend = papers.groupby("year").apply(
        lambda g: pd.Series({
            "avg_authors": g["n_authors"].mean(),
            "pct_multi_institution": (g["n_institutions"] > 1).mean() * 100,
            "pct_international": (g["n_countries"] > 1).mean() * 100,
            "n_papers": len(g),
        })
    ).reset_index()
    trend.to_csv(PROC_DIR / "collaboration_trends_by_year.csv", index=False)
    return trend


def build_author_graph(authorships: pd.DataFrame) -> nx.Graph:
    G = nx.Graph()
    paper_authors = authorships[["paper_id", "author_id", "author_name"]].drop_duplicates()
    for paper_id, g in paper_authors.groupby("paper_id"):
        authors = list(g[["author_id", "author_name"]].itertuples(index=False, name=None))
        for aid, aname in authors:
            if pd.isna(aid):
                continue
            if not G.has_node(aid):
                G.add_node(aid, name=aname)
        for i in range(len(authors)):
            for j in range(i + 1, len(authors)):
                a_id, a_name = authors[i]
                b_id, b_name = authors[j]
                if pd.isna(a_id) or pd.isna(b_id):
                    continue
                if G.has_edge(a_id, b_id):
                    G[a_id][b_id]["weight"] += 1
                else:
                    G.add_edge(a_id, b_id, weight=1)
    return G


def main():
    papers = pd.read_csv(PROC_DIR / "papers.csv")
    authorships = pd.read_csv(PROC_DIR / "authorships.csv")

    # --- collaboration trends ---
    trend = build_trends(papers)
    print("=== Collaboration trends by year ===")
    print(trend.round(1).to_string(index=False))

    # --- co-authorship graph ---
    G = build_author_graph(authorships)
    print(f"\nAuthor graph: {G.number_of_nodes()} authors, {G.number_of_edges()} collaboration edges")

    # top collaborator pairs
    pair_rows = [
        {"author_a": G.nodes[a]["name"], "author_b": G.nodes[b]["name"], "shared_papers": d["weight"]}
        for a, b, d in G.edges(data=True)
    ]
    pairs_df = pd.DataFrame(pair_rows).sort_values("shared_papers", ascending=False)
    pairs_df.to_csv(PROC_DIR / "top_collaborator_pairs.csv", index=False)
    print("\n=== Top 10 collaborator pairs (most shared papers, 2022-2025) ===")
    print(pairs_df.head(10).to_string(index=False))

    # degree / weighted degree
    degree = dict(G.degree())
    weighted_degree = dict(G.degree(weight="weight"))

    # approximate betweenness centrality (bridge-ness within the co-authorship graph itself)
    k = min(500, G.number_of_nodes())
    betweenness = nx.betweenness_centrality(G, k=k, weight=None, seed=42)

    # community detection -> data-driven "schools"
    communities = list(nx.algorithms.community.greedy_modularity_communities(G, weight="weight"))
    author_to_community = {}
    for i, comm in enumerate(communities):
        for node in comm:
            author_to_community[node] = i

    # topic diversity per author (bridges across subject areas, not just within co-authorship graph)
    paper_topic = papers[["paper_id", "level1", "level2"]].dropna(subset=["level2"])
    paper_topic["tag"] = paper_topic["level1"] + " / " + paper_topic["level2"]
    author_paper = authorships[["paper_id", "author_id", "author_name"]].drop_duplicates()
    author_topics = author_paper.merge(paper_topic[["paper_id", "tag"]], on="paper_id")
    diversity = (
        author_topics.groupby(["author_id", "author_name"])["tag"]
        .agg(n_papers="count", n_distinct_topics="nunique", topics=lambda s: "; ".join(sorted(set(s))))
        .reset_index()
    )

    rows = []
    for aid in G.nodes():
        rows.append({
            "author_id": aid,
            "author_name": G.nodes[aid]["name"],
            "n_collaborators": degree.get(aid, 0),
            "weighted_collaborations": weighted_degree.get(aid, 0),
            "betweenness_bridge_score": round(betweenness.get(aid, 0), 5),
            "community_id": author_to_community.get(aid),
        })
    author_stats = pd.DataFrame(rows).merge(
        diversity[["author_id", "n_papers", "n_distinct_topics", "topics"]], on="author_id", how="left"
    )
    author_stats.to_csv(PROC_DIR / "author_network_stats.csv", index=False)

    print(f"\n{len(communities)} collaboration communities detected (data-driven 'schools')")
    print("\n=== Top 10 authors by betweenness (bridge across the co-authorship graph) ===")
    print(author_stats.sort_values("betweenness_bridge_score", ascending=False).head(10)[
        ["author_name", "n_collaborators", "betweenness_bridge_score", "n_papers", "community_id"]
    ].to_string(index=False))

    print("\n=== Top 10 authors by topic diversity (>=2 papers, spans most level2 subjects) ===")
    print(author_stats[author_stats.n_papers >= MIN_PAPERS_FOR_BRIDGE_STATS].sort_values(
        "n_distinct_topics", ascending=False
    ).head(10)[["author_name", "n_papers", "n_distinct_topics", "topics"]].to_string(index=False))

    # community summaries: size, dominant institutions, dominant topics
    comm_rows = []
    inst_by_author = authorships.dropna(subset=["institution_id"])[["author_id", "institution_name"]].drop_duplicates()
    for i, comm in enumerate(communities):
        if len(comm) < 3:
            continue
        members = pd.DataFrame({"author_id": list(comm)})
        insts = members.merge(inst_by_author, on="author_id")["institution_name"].value_counts().head(3)
        topics = author_stats[author_stats.author_id.isin(comm)]["topics"].str.split("; ").explode().value_counts().head(3)
        comm_rows.append({
            "community_id": i,
            "size": len(comm),
            "top_institutions": ", ".join(f"{k} ({v})" for k, v in insts.items()),
            "top_topics": ", ".join(f"{k} ({v})" for k, v in topics.items()),
        })
    comm_df = pd.DataFrame(comm_rows).sort_values("size", ascending=False)
    comm_df.to_csv(PROC_DIR / "collaboration_communities.csv", index=False)

    print("\n=== Top 10 largest collaboration communities ('schools') ===")
    print(comm_df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
