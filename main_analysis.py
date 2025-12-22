import pandas as pd
import os
import glob

# Configuration
DATA_DIR = "collect_data/data"

def check_data_readiness():
    print("🕵️‍♂️  Vérification des données pour l'Analyse...")
    
    # On cherche tous les fichiers CSV
    all_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    
    if not all_files:
        print("❌ CRITIQUE : Aucun fichier CSV trouvé ! Vérifie le dossier.")
        return

    print(f"✅ Trouvé {len(all_files)} fichiers de données.")
    
    # On va essayer d'en ouvrir un de chaque langue pour voir
    langues_test = ['en', 'fr', 'es']
    
    total_tweets = 0
    
    for csv_file in all_files:
        try:
            df = pd.read_csv(csv_file)
            total_tweets += len(df)
        except Exception as e:
            print(f"   ⚠️ Fichier illisible : {csv_file} ({e})")

    print(f"📊 Volume total de données : {total_tweets} tweets prêts à être analysés.")
    
    if total_tweets > 2000:
        print("\n🟢 FEU VERT : Tu as assez de données pour lancer le modèle NLP (BERT).")
    else:
        print("\n🟠 ATTENTION : Volume un peu faible, mais suffisant pour tester le code.")

if __name__ == "__main__":
    check_data_readiness()