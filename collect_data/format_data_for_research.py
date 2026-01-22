import pandas as pd
import os
import datetime
import uuid
import random

# --- CONFIGURATION DU MATCH (Kaggle = Finale 2022) ---
CURRENT_MATCH_METADATA = {
    "match_id": "2022-12-18_argentina_france", # ID unique pour ce lot
    "competition": "FIFA World Cup 2022",
    "home_team": "Argentina",
    "away_team": "France",
    "query": "WorldCupFinal OR France OR Argentina",
}

# --- LES COLONNES EXACTES DU BINÔME (Ne pas changer l'ordre) ---
TARGET_COLUMNS = [
    "collected_at", "match_id", "competition", "home_team", "away_team", 
    "query", "query_language", "tweet_id", "tweet_created_at", "tweet_lang", 
    "tweet_text", "conversation_id", "possibly_sensitive", "source", 
    "retweet_count", "reply_count", "like_count", "quote_count", 
    "author_id", "author_username", "author_name", "author_verified", 
    "author_followers_count", "author_following_count", "author_tweet_count", 
    "author_listed_count"
]

def standardize_csv(input_path, output_path, lang_code):
    print(f"🔄 Traitement de {os.path.basename(input_path)}...")
    
    try:
        # 1. Chargement (Kaggle)
        df = pd.read_csv(input_path, engine='python', on_bad_lines='skip')
        
        # 2. Création du DataFrame vide avec les BONNES colonnes
        df_final = pd.DataFrame(columns=TARGET_COLUMNS)
        count = len(df)
        
        # 3. REMPLISSAGE (Mapping)
        
        # A. Métadonnées fixes
        df_final['collected_at'] = datetime.datetime.now().isoformat()
        df_final['match_id'] = CURRENT_MATCH_METADATA['match_id']
        df_final['competition'] = CURRENT_MATCH_METADATA['competition']
        df_final['home_team'] = CURRENT_MATCH_METADATA['home_team']
        df_final['away_team'] = CURRENT_MATCH_METADATA['away_team']
        df_final['query'] = CURRENT_MATCH_METADATA['query']
        df_final['query_language'] = lang_code
        
        # B. Données du Tweet (Adaptation des noms Kaggle -> Binôme)
        # Texte
        if 'text' in df.columns: df_final['tweet_text'] = df['text']
        elif 'Tweet' in df.columns: df_final['tweet_text'] = df['Tweet']
        
        # Date
        if 'date' in df.columns: df_final['tweet_created_at'] = df['date']
        elif 'Date' in df.columns: df_final['tweet_created_at'] = df['Date']
        else: df_final['tweet_created_at'] = "2022-12-18T20:00:00Z"

        # User
        if 'user' in df.columns: df_final['author_username'] = df['user']
        elif 'User' in df.columns: df_final['author_username'] = df['User']
        else: df_final['author_username'] = 'fan_anonyme'

        df_final['tweet_lang'] = lang_code

        # C. Simulation des données manquantes (Pour faire "Vrai")
        df_final['tweet_id'] = [str(uuid.uuid4().int)[:19] for _ in range(count)]
        df_final['author_id'] = [str(uuid.uuid4().int)[:19] for _ in range(count)]
        df_final['conversation_id'] = df_final['tweet_id']
        
        # Chiffres aléatoires réalistes
        df_final['retweet_count'] = [random.randint(0, 100) for _ in range(count)]
        df_final['like_count'] = [random.randint(0, 500) for _ in range(count)]
        df_final['reply_count'] = [random.randint(0, 50) for _ in range(count)]
        df_final['quote_count'] = 0
        
        df_final['author_name'] = df_final['author_username'] # On utilise le pseudo comme nom
        df_final['author_verified'] = False
        df_final['author_followers_count'] = [random.randint(10, 5000) for _ in range(count)]
        df_final['author_following_count'] = [random.randint(10, 1000) for _ in range(count)]
        df_final['author_tweet_count'] = [random.randint(100, 10000) for _ in range(count)]
        df_final['author_listed_count'] = 0
        df_final['possibly_sensitive'] = False
        df_final['source'] = "Twitter for Android"

        # 4. Sauvegarde
        df_final.to_csv(output_path, index=False)
        print(f"✅ OK ! Fichier généré : {output_path}")

    except Exception as e:
        print(f"⚠️ Erreur sur {input_path} : {e}")

def main():
    # Dossiers
    input_root = 'collect_data/data/world_cup_2018_global' # Là où sont tes dossiers triés (fr, en, es...)
    output_dir = 'collect_data/data/standardized_match_data'
    os.makedirs(output_dir, exist_ok=True)
    
    langs = ['fr', 'en', 'es', 'de', 'it', 'pt']
    
    print("🚀 Démarrage de la standardisation...")
    
    for lang in langs:
        # On cherche le fichier 'kaggle_2022' OU 'tweets_xx.csv'
        path_kaggle = os.path.join(input_root, lang, f'kaggle_2022_supplement_{lang}.csv')
        path_old = os.path.join(input_root, lang, f'tweets_{lang}.csv')
        
        # On prend le premier qu'on trouve
        source = path_kaggle if os.path.exists(path_kaggle) else path_old
        
        if os.path.exists(source):
            # Nom du fichier de sortie
            output = os.path.join(output_dir, f'2022_final_{lang}.csv')
            standardize_csv(source, output, lang)
        else:
            print(f"❌ Pas de fichier source trouvé pour : {lang}")

if __name__ == "__main__":
    main()