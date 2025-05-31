import pandas as pd
from datetime import datetime

# Charger le fichier CSV
df = pd.read_csv("symplectic_geometry_articles.csv")

# Nettoyage
df = df.fillna("null")
df["published_date"] = pd.to_datetime(df["published_date"])
df = df.sort_values(by="published_date", ascending=False)

# Colonnes formatées
df["Publish Date"] = df["published_date"].dt.strftime("**%Y-%m-%d**")
df["Title"] = df["title"].apply(lambda t: f"**{t}**")
df["PDF"] = df["pdf"].apply(lambda url: f"[{url.split('/')[-1]}]({url})" if url != "null" else "null")
df["Code"] = "null"  # Tu peux ajouter des liens vers des dépôts GitHub si tu veux

# Colonnes dans l’ordre souhaité
df_final = df[["Publish Date", "Title", "authors", "PDF", "Code"]]
df_final.columns = ["Publish Date", "Title", "Authors", "PDF", "Code"]

# Générer README.md
with open("README.md", "w", encoding="utf-8") as f:
    f.write("# SymplecticGeometryHub\n\n")
    f.write(f"> Automatically updated on {datetime.today().strftime('%Y.%m.%d')}\n\n")
    f.write("""<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href=#symplectic-geometry,-hamiltonian-mechanics,-poisson-structures>Symplectic Geometry, Hamiltonian Mechanics, Poisson Structures</a></li>
  </ol>
</details>\n\n""")
    f.write("## Symplectic Geometry, Hamiltonian Mechanics, Poisson Structures\n\n")
    f.write(df_final.to_markdown(index=False))
    f.write("\n\n---")

# Générer index.html
with open("index.html", "w", encoding="utf-8") as f:
    f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>SymplecticGeometryHub</title>
  <style>
    body {{ font-family: sans-serif; padding: 2rem; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
    th {{ background-color: #f2f2f2; }}
  </style>
</head>
<body>
  <h1>SymplecticGeometryHub</h1>
  <p><em>Automatically updated on {datetime.today().strftime('%Y.%m.%d')}</em></p>
  <h2>Symplectic Geometry, Hamiltonian Mechanics, Poisson Structures</h2>
  {df_final.to_html(index=False, escape=False)}
</body>
</html>""")
