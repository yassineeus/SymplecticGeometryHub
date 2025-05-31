import pandas as pd
from datetime import datetime

# Charger le fichier CSV
df = pd.read_csv("symplectic_geometry_articles.csv")
df = df.fillna("null")
df = df.sort_values(by="published_date", ascending=False)

# Générer les lignes HTML pour le tableau
rows_html = ""
for _, row in df.iterrows():
    rows_html += f"""        <tr>
            <td>{row['published_date']}</td>
            <td>{row['authors']}</td>
            <td>{row['title']}</td>
            <td><a href="{row['url']}">{row['id']}</a></td>
        </tr>\n"""

# Charger le modèle HTML
with open("index_template.html", "r", encoding="utf-8") as f:
    template = f.read()

# Remplacer la zone d'injection
final_html = template.replace("<!--ARTICLE_TBODY_HERE-->", rows_html)

# Sauvegarder la version générée
with open("index.html", "w", encoding="utf-8") as f:
    f.write(final_html)
