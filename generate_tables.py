import pandas as pd
from datetime import datetime
import os
import html

def generate_html_table():
    """Génère le tableau HTML à partir du CSV"""
    try:
        # Fichiers
        csv_file = "symplectic_geometry_articles.csv"
        template_file = "index_template.html"
        output_file = "index.html"
        
        print(f"📊 Chargement des données depuis {csv_file}...")
        
        # Vérifier que le CSV existe
        if not os.path.exists(csv_file):
            print(f"❌ Erreur: {csv_file} n'existe pas!")
            return False
        
        # Charger le CSV
        df = pd.read_csv(csv_file, encoding='utf-8')
        print(f"✅ {len(df)} articles chargés")
        
        # Vérifier les colonnes nécessaires
        required_columns = ['published_date', 'authors', 'title', 'url', 'id']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ Colonnes manquantes: {missing_columns}")
            print(f"Colonnes disponibles: {list(df.columns)}")
            return False
        
        # Nettoyer les données
        df = df.fillna("Non spécifié")
        
        # Trier par date
        try:
            df['published_date'] = pd.to_datetime(df['published_date'], errors='coerce')
            df = df.sort_values(by="published_date", ascending=False)
            # Formatter les dates pour l'affichage
            df['published_date'] = df['published_date'].dt.strftime('%Y-%m-%d')
            df['published_date'] = df['published_date'].fillna("Date inconnue")
            print("✅ Données triées par date")
        except Exception as e:
            print(f"⚠️ Problème avec le tri des dates: {e}")
        
        # Générer les lignes HTML
        print("🔄 Génération des lignes HTML...")
        rows_html = ""
        
        for index, row in df.iterrows():
            # Échapper le HTML pour la sécurité
            published_date = html.escape(str(row['published_date']))
            authors = html.escape(str(row['authors']))
            title = html.escape(str(row['title']))
            url = html.escape(str(row['url']))
            article_id = html.escape(str(row['id']))
            
            # Générer la ligne HTML
            row_html = f"""        <tr>
            <td>{published_date}</td>
            <td>{authors}</td>
            <td>{title}</td>
            <td><a href="{url}" target="_blank">{article_id}</a></td>
        </tr>\n"""
            
            rows_html += row_html
        
        print(f"✅ {len(df)} lignes HTML générées")
        
        # Charger le template
        print(f"📝 Chargement du template {template_file}...")
        
        if not os.path.exists(template_file):
            print(f"❌ Erreur: {template_file} n'existe pas!")
            return False
        
        with open(template_file, "r", encoding="utf-8") as f:
            template_content = f.read()
        
        # Vérifier la présence du marker
        marker = "<!--ARTICLE_TBODY_HERE-->"
        if marker not in template_content:
            print(f"❌ Erreur: Marker '{marker}' non trouvé dans le template!")
            return False
        
        print("✅ Template chargé et marker trouvé")
        
        # Remplacer le marker par les données
        final_html = template_content.replace(marker, rows_html)
        
        # Vérifier que le remplacement a eu lieu
        if marker in final_html:
            print("❌ Erreur: Le marker n'a pas été remplacé!")
            return False
        
        # Sauvegarder le fichier final
        print(f"💾 Sauvegarde vers {output_file}...")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(final_html)
        
        # Vérifier le résultat
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"✅ Fichier généré avec succès!")
            print(f"📄 Taille: {file_size:,} octets")
            print(f"📊 Articles: {len(df)}")
            return True
        else:
            print("❌ Erreur: Fichier de sortie non créé!")
            return False
            
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def update_last_update_time():
    """Met à jour le timestamp dans le HTML si nécessaire"""
    try:
        output_file = "index.html"
        if os.path.exists(output_file):
            with open(output_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Remplacer le timestamp si présent
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if 'id="lastUpdate"' in content:
                # Pattern plus flexible pour le remplacement
                import re
                pattern = r'(<span id="lastUpdate">)[^<]*(</span>)'
                replacement = f'\\g<1>{current_time}\\g<2>'
                content = re.sub(pattern, replacement, content)
                
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"🕒 Timestamp mis à jour: {current_time}")
    except Exception as e:
        print(f"⚠️ Erreur mise à jour timestamp: {e}")

def main():
    """Fonction principale"""
    print("🚀 Début de la génération HTML...")
    print("=" * 50)
    
    success = generate_html_table()
    
    if success:
        update_last_update_time()
        print("=" * 50)
        print("🎉 Génération terminée avec succès!")
        print("👀 Ouvrez index.html dans votre navigateur pour voir le résultat")
    else:
        print("=" * 50)
        print("❌ Échec de la génération!")
        print("💡 Utilisez debug_generate_html_table() pour plus de détails")
    
    return success

if __name__ == "__main__":
    main()
