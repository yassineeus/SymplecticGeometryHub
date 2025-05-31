import arxiv
import pandas as pd
import datetime
import time
import re

# Liste de requêtes de recherche pour la géométrie symplectique
SEARCH_QUERIES = [
    '"symplectic geometry"',
    '"symplectic manifold"',
    '"symplectic structure"',
    '"coisotropic submanifold"',
    '"lagrangian submanifold"',
    '"Poisson geometry"',
    '"Dirac structure"',
    '"moment map"',
    '"symplectic reduction"',
    '"Hamiltonian system"',
    '"Marsden–Weinstein reduction"',
]

CATEGORIES = [
    'math.SG',
    'math.DG',
    'math-ph',
    'math.QA',
    'math.AG'
]

MAX_RESULTS = 150
RESULTS_FILE = "symplectic_geometry_articles.csv"
INDEX_FILE = "index.md"

def build_query(term):
    cats = " OR ".join([f"cat:{c}" for c in CATEGORIES])
    return f"({term}) AND ({cats})"

def fetch_articles():
    all_results = []
    client = arxiv.Client(page_size=100, delay_seconds=3)
    for term in SEARCH_QUERIES:
        query = build_query(term)
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
            print(f"Erreur avec la requête '{term}': {e}")
    # Supprimer doublons
    return list({r.get_short_id(): r for r in all_results}.values())

def extract_info(result):
    return {
        "id": result.get_short_id(),
        "title": result.title.replace('\n', ' ').strip(),
        "authors": ", ".join(a.name for a in result.authors),
        "published_date": result.published.strftime("%Y-%m-%d"),
        "url": result.entry_id,
        "pdf": result.pdf_url
    }

def save_to_csv(results):
    articles = [extract_info(r) for r in results]
    df = pd.DataFrame(articles).sort_values(by="published_date", ascending=False)
    df.to_csv(RESULTS_FILE, index=False)
    return df

def generate_index_md(df):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write("# Collection of Articles on Symplectic Geometry\n\n")
        f.write("This list is automatically updated from [arXiv.org](https://arxiv.org) with recent papers related to symplectic geometry, coisotropic submanifolds, Poisson structures, and related topics.\n\n")
        f.write("| Date | Authors | Title | Link |\n")
        f.write("|------|---------|-------|------|\n")

        for _, row in df.head(30).iterrows():
            title = row['title'].replace("|", "\\|")
            authors = row['authors'].replace("|", "\\|")
            date = row['published_date']
            link = f"[arXiv:{row['id']}]({row['url']})"
            f.write(f"| {date} | {authors} | {title} | {link} |\n")

def main():
    print("🔍 Fetching symplectic geometry articles from arXiv...")
    results = fetch_articles()
    df = save_to_csv(results)
    generate_index_md(df)
    print(f"✅ {len(df)} articles saved to CSV and index.md generated.")

if __name__ == "__main__":
    main()
