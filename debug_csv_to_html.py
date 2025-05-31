import pandas as pd
from datetime import datetime
import os
import html

def debug_generate_html_table():
    print("=== DÉBOGAGE DU GÉNÉRATEUR HTML ===")
    
    # 1. Vérifier les fichiers
    csv_file = "symplectic_geometry_articles.csv"
    template_file = "index_template.html"
    
    print(f"📁 Vérification des fichiers...")
    print(f"   CSV exists: {os.path.exists(csv_file)}")
    print(f"   Template exists: {os.path.exists(template_file)}")
    
    if not os.path.exists(csv_file):
        print("❌ ERREUR: Fichier CSV manquant!")
        return False
    
    if not os.path.exists(template_file):
        print("❌ ERREUR: Fichier template manquant!")
        return False
    
    # 2. Analyser le CSV
    print(f"\n📊 Analyse du CSV...")
    try:
        df = pd.read_csv(csv_file, encoding='utf-8')
        print(f"   Lignes dans le CSV: {len(df)}")
        print(f"   Colonnes: {list(df.columns)}")
        print(f"   Premières lignes:")
        print(df.head(3).to_string())
        
        # Vérifier les colonnes nécessaires
        required_columns = ['published_date', 'authors', 'title', 'url', 'id']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"❌ Colonnes manquantes: {missing_columns}")
            return False
        else:
            print(f"✅ Toutes les colonnes nécessaires sont présentes")
            
    except Exception as e:
        print(f"❌ ERREUR lors de la lecture du CSV: {e}")
        return False
    
    # 3. Analyser le template
    print(f"\n📝 Analyse du template...")
    try:
        with open(template_file, "r", encoding="utf-8") as f:
            template_content = f.read()
        
        marker = "<!--ARTICLE_TBODY_HERE-->"
        marker_found = marker in template_content
        print(f"   Taille du template: {len(template_content)} caractères")
        print(f"   Marker trouvé: {marker_found}")
        
        if marker_found:
            marker_position = template_content.find(marker)
            print(f"   Position du marker: {marker_position}")
            # Afficher le contexte autour du marker
            start = max(0, marker_position - 50)
            end = min(len(template_content), marker_position + len(marker) + 50)
            context = template_content[start:end]
            print(f"   Contexte: ...{context}...")
        else:
            print(f"❌ ERREUR: Marker '{marker}' non trouvé dans le template!")
            return False
            
    except Exception as e:
        print(f"❌ ERREUR lors de la lecture du template: {e}")
        return False
    
    # 4. Traitement des données
    print(f"\n🔄 Traitement des données...")
    df = df.fillna("Non spécifié")
    
    # Trier par date
    try:
        df['published_date'] = pd.to_datetime(df['published_date'], errors='coerce')
        df = df.sort_values(by="published_date", ascending=False)
        df['published_date'] = df['published_date'].dt.strftime('%Y-%m-%d')
        df['published_date'] = df['published_date'].fillna("Date inconnue")
        print(f"   Tri des dates: ✅")
    except Exception as e:
        print(f"   Problème avec les dates: {e}")
    
    # 5. Générer le HTML
    print(f"\n🛠️ Génération du HTML...")
    rows_html = ""
    processed_count = 0
    
    for index, row in df.iterrows():
        try:
            # Échapper le HTML
            published_date = html.escape(str(row['published_date']))
            authors = html.escape(str(row['authors']))
            title = html.escape(str(row['title']))
            url = html.escape(str(row['url']))
            article_id = html.escape(str(row['id']))
            
            row_html = f"""        <tr>
            <td>{published_date}</td>
            <td>{authors}</td>
            <td>{title}</td>
            <td><a href="{url}" target="_blank">{article_id}</a></td>
        </tr>\n"""
            
            rows_html += row_html
            processed_count += 1
            
            # Afficher les premières lignes pour débogage
            if processed_count <= 3:
                print(f"   Ligne {processed_count}: {published_date} | {authors[:30]}... | {title[:30]}...")
                
        except Exception as e:
            print(f"   ❌ Erreur ligne {index}: {e}")
            continue
    
    print(f"   Lignes HTML générées: {processed_count}")
    print(f"   Taille du HTML généré: {len(rows_html)} caractères")
    
    if processed_count == 0:
        print("❌ ERREUR: Aucune ligne HTML générée!")
        return False
    
    # 6. Générer le fichier final
    print(f"\n📄 Génération du fichier final...")
    try:
        final_html = template_content.replace(marker, rows_html)
        
        # Vérifier que le remplacement a eu lieu
        if marker in final_html:
            print(f"❌ ERREUR: Le marker n'a pas été remplacé!")
            return False
        
        output_file = "index.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(final_html)
        
        # Vérifier le fichier généré
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"   ✅ Fichier généré: {output_file}")
            print(f"   Taille: {file_size} octets")
            
            # Vérifier qu'il y a des données dans le tableau
            with open(output_file, "r", encoding="utf-8") as f:
                content = f.read()
                tr_count = content.count("<tr>") - 1  # -1 pour l'en-tête
                print(f"   Lignes de données dans le tableau: {tr_count}")
            
            return True
        else:
            print(f"❌ ERREUR: Fichier non créé!")
            return False
            
    except Exception as e:
        print(f"❌ ERREUR lors de la génération: {e}")
        return False

def create_test_csv():
    """Crée un CSV de test si nécessaire"""
    test_data = {
        'published_date': ['2024-01-15', '2024-01-14', '2024-01-13'],
        'authors': ['John Doe, Jane Smith', 'Alice Johnson', 'Bob Wilson'],
        'title': ['Test Article 1', 'Test Article 2', 'Test Article 3'],
        'url': ['https://arxiv.org/abs/2401.1234', 'https://arxiv.org/abs/2401.5678', 'https://arxiv.org/abs/2401.9012'],
        'id': ['2401.1234', '2401.5678', '2401.9012']
    }
    
    df = pd.DataFrame(test_data)
    df.to_csv("test_symplectic_geometry_articles.csv", index=False)
    print("✅ CSV de test créé: test_symplectic_geometry_articles.csv")

if __name__ == "__main__":
    print("🚀 DÉBUT DU DÉBOGAGE\n")
    
    # Proposer de créer un CSV de test si le principal n'existe pas
    if not os.path.exists("symplectic_geometry_articles.csv"):
        print("⚠️ CSV principal manquant. Création d'un CSV de test...")
        create_test_csv()
        # Modifier temporairement le nom du fichier pour le test
        global csv_file
        csv_file = "test_symplectic_geometry_articles.csv"
    
    success = debug_generate_html_table()
    
    print(f"\n{'='*50}")
    if success:
        print("🎉 SUCCÈS! Le fichier HTML a été généré.")
        print("📋 Vérifiez le fichier index.html dans votre navigateur.")
    else:
        print("❌ ÉCHEC! Consultez les messages ci-dessus pour identifier le problème.")
    print(f"{'='*50}")
