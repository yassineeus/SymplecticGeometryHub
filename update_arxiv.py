# Here's a complete and advanced version of the arXiv scraper script adapted for symplectic geometry.
# This version includes extended queries, keyword matching, and organized output for publication tracking.

import arxiv
import pandas as pd
import datetime
import os
import yaml
import time
import re
from tqdm import tqdm
from pathlib import Path

# Keywords for symplectic geometry and related topics
SEARCH_QUERIES = [
    '"symplectic geometry"',
    '"symplectic manifold"',
    '"symplectic structure"',
    '"lagrangian submanifold"',
    '"coisotropic submanifold"',
    '"moment map"',
    '"symplectic reduction"',
    '"hamiltonian action"',
    '"symplectic groupoid"',
    '"Poisson geometry"',
    '"Dirac structure"',
    '"Marsden–Weinstein reduction"',
    '"pre-symplectic geometry"',
    '"shifted symplectic structure"',
    '"derived symplectic geometry"',
    '"symplectic foliation"',
    '"symplectic Lie algebroid"',
    '"Poisson sigma model"',
    '"coisotropic brane"',
]

# Categories to target
CATEGORIES = [
    'math.SG',  # Symplectic Geometry
    'math.DG',  # Differential Geometry
    'math.AG',  # Algebraic Geometry
    'math-ph',  # Mathematical Physics
    'math.QA',  # Quantum Algebra
]

# Files
RESULTS_FILE = "symplectic_geometry_articles.csv"
README_FILE = "README.md"
CONFIG_FILE = "config_symplectic.yaml"

MAX_RESULTS = 150

def build_query(term, categories):
    cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
    return f"({term}) AND ({cat_query})"

def fetch_articles():
    all_results = []
    client = arxiv.Client(page_size=100, delay_seconds=3, num_retries=5)
    
    for query_term in tqdm(SEARCH_QUERIES, desc="Fetching symplectic articles"):
        query = build_query(query_term, CATEGORIES)
        search = arxiv.Search(
            query=query,
            max_results=MAX_RESULTS,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        try:
            results = list(client.results(search))
            all_results.extend(results)
            time.sleep(2)
        except Exception as e:
            print(f"Error fetching for term {query_term}: {e}")
    
    unique = {r.get_short_id(): r for r in all_results}
    return list(unique.values())

def extract_info(result):
    return {
        "id": result.get_short_id(),
        "title": result.title,
        "authors": ", ".join(a.name for a in result.authors),
        "published": result.published.strftime("%Y-%m-%d"),
        "updated": result.updated.strftime("%Y-%m-%d") if hasattr(result, 'updated') else '',
        "summary": result.summary,
        "categories": ", ".join(result.categories),
        "url": result.entry_id,
        "pdf": result.pdf_url
    }

def save_to_csv(results):
    articles = [extract_info(r) for r in results]
    df = pd.DataFrame(articles).sort_values(by="published", ascending=False)
    df.to_csv(RESULTS_FILE, index=False)
    return df

def generate_readme(df):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(f"# Symplectic Geometry Article Tracker\n\n")
        f.write(f"Last updated: **{now}**\n\n")
        f.write(f"Total articles: **{len(df)}**\n\n")
        f.write("## Latest Articles\n\n")
        f.write("| Date | Title | Authors | PDF |\n")
        f.write("|------|-------|---------|-----|\n")
        for _, row in df.head(10).iterrows():
            f.write(f"| {row['published']} | {row['title'].replace('|', ' ')} | {row['authors']} | [PDF]({row['pdf']}) |\n")

def main():
    print("Starting Symplectic Geometry Article Collection...")
    results = fetch_articles()
    df = save_to_csv(results)
    generate_readme(df)
    print(f"Done. {len(df)} articles saved to {RESULTS_FILE}")

main()
