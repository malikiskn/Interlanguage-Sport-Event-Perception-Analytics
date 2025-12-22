import pandas as pd
import os
from langdetect import detect, LangDetectException

# --- CONFIGURATION ---
# Le nom exact de ton nouveau fichier
INPUT_FILE = "collect_data/tweets_football.csv" 
# Si le fichier est au même niveau que le script, tu peux mettre juste "tweets_football.csv"
if not os.path.exists(INPUT_FILE):
    INPUT_FILE = "tweets_football.csv"

OUTPUT_DIR = "collect_data/data"

# Tes 8 Matchs Virtuels (Stratégie README)
MATCHS_A_EXTRAIRE = [
    {"id": "2022-12-18_france_argentina", "terms": ["France", "Mbappe", "Argentina", "Messi"], "langs": ["fr", "es", "en"]},
    {"id": "2022-12-14_france_morocco",   "terms": ["France", "Morocco", "Maroc"], "langs": ["fr", "en"]}, 
    {"id": "2022-12-10_england_france",   "terms": ["England", "France", "Kane"], "langs": ["en", "fr", "es"]},
    {"id": "2022-12-09_netherlands_argentina", "terms": ["Netherlands", "Argentina"], "langs": ["nl", "es", "en"]},
    {"id": "2022-12-06_morocco_spain",    "terms": ["Morocco", "Spain", "Espana"], "langs": ["en", "es"]},
    {"id": "2022-12-01_costarica_germany", "terms": ["Germany", "Costa Rica"], "langs": ["de", "es", "en"]},
    {"id": "2022-11-27_spain_germany",    "terms": ["Spain", "Germany", "Deutschland"], "langs": ["es", "de", "fr"]},
    {"id": "2022-11-23_germany_japan",    "terms": ["Germany", "Japan"], "langs": ["de", "en"]} 
]

TARGET_PER_LANG = 170

def detect_language_safe(text):
    """Essaie de deviner la langue du tweet."""
    try:
        if not isinstance(text, str) or len(text) < 5:
            return "unknown"
        return detect(text)
    except LangDetectException:
        return "unknown"

def clean_and_convert():
    print(f"⏳ Chargement du fichier '{INPUT_FILE}'...")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ ERREUR: Le fichier '{INPUT_FILE}' est introuvable.")
        print("   Vérifie qu'il est bien dans le dossier collect_data ou à côté du script.")
        return

    try:
        # Lecture du CSV (parfois le séparateur est ; ou , on laisse pandas deviner)
        df = pd.read_csv(INPUT_FILE)
    except Exception as e:
        print(f"❌ Erreur de lecture : {e}")
        return

    print(f"   ✅ Fichier chargé : {len(df)} lignes.")
    print(f"   ℹ️  Colonnes trouvées : {list(df.columns)}")
    
    # 1. MAPPING DES COLONNES (Adapté à ton fichier tweets_football.csv)
    # Tes colonnes sont : Date, User, Tweet
    col_text = 'Tweet'
    col_date = 'Date'
    
    if col_text not in df.columns:
        print("❌ ERREUR: Colonne 'Tweet' non trouvée. Vérifie le CSV.")
        return

    # On prépare une colonne langue vide
    print("   ℹ️  Détection des langues configurée (automatique).")
    df['detected_lang'] = None 

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for match in MATCHS_A_EXTRAIRE:
        print(f"\n🏟️  Traitement du match : {match['id']}...")
        
        # Filtrage par mots-clés
        terms = match['terms']
        # On ne garde que les tweets qui contiennent les mots clés
        mask = df[col_text].str.contains('|'.join(terms), case=False, na=False)
        df_match = df[mask].copy()
        
        count_found = len(df_match)
        if count_found == 0:
            print("   ⚠️ Aucun tweet trouvé pour ce match.")
            continue
        
        print(f"      -> {count_found} tweets candidats trouvés. Analyse des langues...")

        # DÉTECTION DE LANGUE (Uniquement sur les tweets filtrés pour aller vite)
        # Ça peut prendre quelques secondes
        df_match['detected_lang'] = df_match[col_text].apply(detect_language_safe)

        for lang in match['langs']:
            # Filtrage par langue
            df_lang = df_match[df_match['detected_lang'] == lang]
            count = len(df_lang)

            if count > 0:
                # Échantillonnage (on en prend 170 max)
                sample = df_lang.sample(n=min(count, TARGET_PER_LANG))
                
                # Création du fichier final au format attendu par ton projet
                final_df = pd.DataFrame({
                    'tweet_text': sample[col_text],
                    'tweet_lang': sample['detected_lang'],
                    'tweet_created_at': sample[col_date] if col_date in df.columns else "2022-12-01T00:00:00Z",
                    'match_id': match['id']
                })
                
                filename = f"{OUTPUT_DIR}/{match['id']}_{lang}.csv"
                final_df.to_csv(filename, index=False)
                print(f"   -> 💾 OK : {filename} ({len(final_df)} tweets)")
            else:
                print(f"   -> ⚠️ Pas de tweets trouvés pour la langue '{lang}'")

if __name__ == "__main__":
    clean_and_convert()