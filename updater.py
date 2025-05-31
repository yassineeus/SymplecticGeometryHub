# Script de mise à jour automatique pour la collection d'articles de géométrie symplectique
# Created by Yassine Ait Mohamed

import arxiv
import datetime
import os
import json
import schedule
import time
from pathlib import Path

# Configuration
SEARCH_QUERIES = [
    '"symplectic geometry"',
    '"symplectic manifold"',
    '"symplectic structure"',
    '"lagrangian submanifold"',
    '"moment map"',
    '"Poisson geometry"'
]

CATEGORIES = [
    'math.SG',  # Symplectic Geometry
    'math.DG',  # Differential Geometry
    'math.AG',  # Algebraic Geometry
    'math-ph',  # Mathematical Physics
]

MAX_ARTICLES = 50  # Nombre maximum d'articles à afficher
DELAY_BETWEEN_REQUESTS = 3

def fetch_recent_articles(days_back=30):
    """Récupère les articles récents depuis arXiv"""
    print(f"🔍 Recherche d'articles des {days_back} derniers jours...")
    
    all_results = []
    client = arxiv.Client(page_size=100, delay_seconds=DELAY_BETWEEN_REQUESTS)
    
    # Date range
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=days_back)
    
    for query_term in SEARCH_QUERIES:
        cat_query = " OR ".join([f"cat:{cat}" for cat in CATEGORIES])
        query = f"({query_term}) AND ({cat_query})"
        
        search = arxiv.Search(
            query=query,
            max_results=200,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        try:
            results = list(client.results(search))
            all_results.extend(results)
            time.sleep(DELAY_BETWEEN_REQUESTS)
        except Exception as e:
            print(f"❌ Erreur pour la requête {query_term}: {e}")
    
    # Remove duplicates and filter by date
    unique_results = {}
    for result in all_results:
        if result.published >= start_date:
            unique_results[result.get_short_id()] = result
    
    # Sort by date (newest first)
    sorted_results = sorted(unique_results.values(), 
                          key=lambda x: x.published, 
                          reverse=True)
    
    return sorted_results[:MAX_ARTICLES]

def generate_html_table(articles):
    """Génère le tableau HTML des articles"""
    rows = []
    
    for article in articles:
        date = article.published.strftime('%Y-%m-%d')
        authors = ", ".join([author.name for author in article.authors])
        title = article.title.strip()
        arxiv_id = article.get_short_id()
        url = article.entry_id
        
        row = f"""            <tr>
                <td>{date}</td>
                <td>{authors}</td>
                <td>{title}</td>
                <td><a href="{url}">arXiv:{arxiv_id}</a></td>
            </tr>"""
        rows.append(row)
    
    return '\n'.join(rows)

def update_html_file(articles):
    """Met à jour le fichier index.html"""
    print("📝 Mise à jour du fichier HTML...")
    
    table_content = generate_html_table(articles)
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Collection of Articles on Symplectic Geometry</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #ffffff;
        }}
        
        h1 {{
            color: #24292e;
            border-bottom: 1px solid #e1e4e8;
            padding-bottom: 10px;
        }}
        
        p {{
            color: #586069;
            margin-bottom: 16px;
        }}
        
        .update-info {{
            background-color: #f6f8fa;
            padding: 10px;
            border-radius: 6px;
            margin-bottom: 20px;
            border-left: 4px solid #0366d6;
        }}
        
        a {{
            color: #0366d6;
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        th, td {{
            border: 1px solid #d0d7de;
            padding: 8px 12px;
            text-align: left;
        }}
        
        th {{
            background-color: #f6f8fa;
            font-weight: 600;
        }}
        
        tbody tr:nth-child(even) {{
            background-color: #f6f8fa;
        }}
        
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e1e4e8;
            text-align: center;
            color: #586069;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <h1>Collection of Articles on Symplectic Geometry</h1>
    
    <p>This list is automatically updated from <a href="https://arxiv.org">arXiv.org</a> with recent papers related to symplectic geometry, coisotropic submanifolds, Poisson structures, and related topics.</p>
    
    <div class="update-info">
        <strong>📅 Last updated:</strong> {now} | <strong>📊 Total articles:</strong> {len(articles)}
    </div>
    
    <table>
        <thead>
            <tr>
                <th>Date</th>
                <th>Authors</th>
                <th>Title</th>
                <th>Link</th>
            </tr>
        </thead>
        <tbody>
{table_content}
        </tbody>
    </table>
    
    <div class="footer">
        <p><em>Created by Yassine Ait Mohamed</em></p>
        <p>🤖 Automatically updated every day at 6:00 AM</p>
    </div>
</body>
</html>"""
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"✅ Fichier index.html mis à jour avec {len(articles)} articles")

def save_backup(articles):
    """Sauvegarde les données en JSON"""
    data = {
        'last_update': datetime.datetime.now().isoformat(),
        'total_articles': len(articles),
        'articles': [
            {
                'id': article.get_short_id(),
                'title': article.title,
                'authors': [author.name for author in article.authors],
                'published': article.published.isoformat(),
                'url': article.entry_id
            }
            for article in articles
        ]
    }
    
    with open('articles_backup.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("💾 Sauvegarde créée dans articles_backup.json")

def daily_update():
    """Fonction de mise à jour quotidienne"""
    print("🚀 Début de la mise à jour quotidienne...")
    print("=" * 50)
    
    try:
        # Récupération des articles
        articles = fetch_recent_articles(days_back=30)
        
        if articles:
            # Mise à jour du HTML
            update_html_file(articles)
            
            # Sauvegarde
            save_backup(articles)
            
            print("=" * 50)
            print("✅ Mise à jour terminée avec succès!")
            print(f"📈 {len(articles)} articles traités")
        else:
            print("⚠️ Aucun article trouvé")
            
    except Exception as e:
        print(f"❌ Erreur durante la mise à jour: {e}")

def setup_scheduler():
    """Configure le planificateur pour les mises à jour automatiques"""
    # Mise à jour quotidienne à 6h du matin
    schedule.every().day.at("06:00").do(daily_update)
    
    print("⏰ Planificateur configuré:")
    print("   - Mise à jour quotidienne à 6:00 AM")
    print("   - Appuyez sur Ctrl+C pour arrêter")
    print("=" * 50)
    
    # Premier run immédiatement
    print("🔥 Première exécution...")
    daily_update()
    
    # Boucle principale
    while True:
        schedule.run_pending()
        time.sleep(60)  # Vérifier toutes les minutes

def manual_update():
    """Mise à jour manuelle"""
    print("🔧 Mise à jour manuelle démarrée...")
    daily_update()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "manual":
        # Mise à jour manuelle
        manual_update()
    else:
        # Mode automatique avec scheduler
        try:
            setup_scheduler()
        except KeyboardInterrupt:
            print("\n👋 Arrêt du planificateur...")
            print("Au revoir!")
