import pandas as pd
from datetime import datetime
import os
import html

def generate_html_table():
    try:
        # Vérifier que le fichier CSV existe
        csv_file = "symplectic_geometry_articles.csv"
        if not os.path.exists(csv_file):
            print(f"Erreur: Le fichier {csv_file} n'existe pas.")
            return False
        
        # Charger le fichier CSV
        print("Chargement du fichier CSV...")
        df = pd.read_csv(csv_file, encoding='utf-8')
        
        # Vérifier les colonnes nécessaires
        required_columns = ['published_date', 'authors', 'title', 'url', 'id']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Erreur: Colonnes manquantes dans le CSV: {missing_columns}")
            print(f"Colonnes disponibles: {list(df.columns)}")
            return False
        
        # Nettoyer les données
        df = df.fillna("Non spécifié")
        
        # Trier par date de publication (format supposé: YYYY-MM-DD)
        try:
            df['published_date'] = pd.to_datetime(df['published_date'], errors='coerce')
            df = df.sort_values(by="published_date", ascending=False)
            # Reformater les dates pour l'affichage
            df['published_date'] = df['published_date'].dt.strftime('%Y-%m-%d')
            df['published_date'] = df['published_date'].fillna("Date inconnue")
        except Exception as e:
            print(f"Attention: Problème avec le tri des dates: {e}")
            df = df.sort_values(by="published_date", ascending=False)
        
        # Générer les lignes HTML pour le tableau
        print("Génération des lignes HTML...")
        rows_html = ""
        for index, row in df.iterrows():
            # Échapper le HTML pour éviter les problèmes d'injection
            published_date = html.escape(str(row['published_date']))
            authors = html.escape(str(row['authors']))
            title = html.escape(str(row['title']))
            url = html.escape(str(row['url']))
            article_id = html.escape(str(row['id']))
            
            rows_html += f"""        <tr>
            <td>{published_date}</td>
            <td>{authors}</td>
            <td>{title}</td>
            <td><a href="{url}" target="_blank">{article_id}</a></td>
        </tr>\n"""
        
        # Vérifier que le template existe
        template_file = "index_template.html"
        if not os.path.exists(template_file):
            print(f"Erreur: Le fichier template {template_file} n'existe pas.")
            # Créer un template basique
            print("Création d'un template HTML basique...")
            create_basic_template()
        
        # Charger le modèle HTML
        print("Chargement du template HTML...")
        with open(template_file, "r", encoding="utf-8") as f:
            template = f.read()
        
        # Vérifier que la zone d'injection existe
        if "<!--ARTICLE_TBODY_HERE-->" not in template:
            print("Erreur: Le marker <!--ARTICLE_TBODY_HERE--> n'existe pas dans le template.")
            return False
        
        # Remplacer la zone d'injection
        final_html = template.replace("<!--ARTICLE_TBODY_HERE-->", rows_html)
        
        # Sauvegarder la version générée
        output_file = "index.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(final_html)
        
        print(f"✅ Fichier HTML généré avec succès: {output_file}")
        print(f"📊 {len(df)} articles traités")
        return True
        
    except FileNotFoundError as e:
        print(f"Erreur: Fichier non trouvé - {e}")
        return False
    except pd.errors.EmptyDataError:
        print("Erreur: Le fichier CSV est vide.")
        return False
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        return False

def create_basic_template():
    """Crée un template HTML basique si il n'existe pas"""
    template_content = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Articles de Géométrie Symplectique</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f8f9fa;
            font-weight: bold;
            color: #333;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        a {
            color: #007bff;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .date-col { width: 12%; }
        .authors-col { width: 25%; }
        .title-col { width: 50%; }
        .id-col { width: 13%; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📐 Articles de Géométrie Symplectique</h1>
        <table>
            <thead>
                <tr>
                    <th class="date-col">Date de Publication</th>
                    <th class="authors-col">Auteurs</th>
                    <th class="title-col">Titre</th>
                    <th class="id-col">Lien</th>
                </tr>
            </thead>
            <tbody>
<!--ARTICLE_TBODY_HERE-->
            </tbody>
        </table>
    </div>
</body>
</html>"""
    
    with open("index_template.html", "w", encoding="utf-8") as f:
        f.write(template_content)
    print("✅ Template HTML basique créé: index_template.html")

# Exécuter la fonction
if __name__ == "__main__":
    print("🚀 Début de la génération HTML...")
    success = generate_html_table()
    if success:
        print("🎉 Traitement terminé avec succès!")
    else:
        print("❌ Échec du traitement. Vérifiez les erreurs ci-dessus.")
