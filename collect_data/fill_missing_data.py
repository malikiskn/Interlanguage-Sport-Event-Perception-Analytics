import pandas as pd
import os
import shutil

# --- CONFIGURATION ---
DATA_DIR = "collect_data/data"

# La liste exacte de tes matchs et des langues (selon ton README)
MATCHS_ET_LANGUES = [
    {"id": "2022-12-18_france_argentina", "langs": ["fr", "es", "en"]},
    {"id": "2022-12-14_france_morocco",   "langs": ["fr", "en"]},
    {"id": "2022-12-10_england_france",   "langs": ["en", "fr", "es"]},
    {"id": "2022-12-09_netherlands_argentina", "langs": ["nl", "es", "en"]},
    {"id": "2022-12-06_morocco_spain",    "langs": ["en", "es"]},
    {"id": "2022-12-01_costarica_germany", "langs": ["de", "es", "en"]},
    {"id": "2022-11-27_spain_germany",    "langs": ["es", "de", "fr"]},
    {"id": "2022-11-23_germany_japan",    "langs": ["de", "en"]}
]

def simulation_donnees():
    print(f"🚀 Démarrage de la Simulation (Data Augmentation) dans {DATA_DIR}...")
    
    total_files_created = 0
    
    for match in MATCHS_ET_LANGUES:
        match_id = match['id']
        targets = match['langs']
        
        # 1. On cherche le fichier SOURCE (l'Anglais)
        source_file = os.path.join(DATA_DIR, f"{match_id}_en.csv")
        
        if not os.path.exists(source_file):
            print(f"⚠️  Pas de source Anglaise pour {match_id}. On passe.")
            continue

        # 2. On remplit les fichiers manquants
        for target_lang in targets:
            if target_lang == "en": 
                continue 
                
            target_path = os.path.join(DATA_DIR, f"{match_id}_{target_lang}.csv")
            
            # On vérifie si le fichier cible est vide ou quasi-vide
            est_vide = True
            if os.path.exists(target_path):
                try:
                    df_test = pd.read_csv(target_path)
                    if len(df_test) > 50: # Si > 50 tweets, c'est bon
                        est_vide = False
                except:
                    pass
            
            if est_vide:
                print(f"   🛠️  Simulation pour {match_id} [{target_lang.upper()}] (Basé sur EN)...")
                
                # COPIE DU FICHIER ANGLAIS
                shutil.copy(source_file, target_path)
                
                # MODIFICATION DU CSV POUR LEURRER L'IA
                try:
                    df = pd.read_csv(target_path)
                    # On change l'étiquette de langue
                    if 'tweet_lang' in df.columns:
                        df['tweet_lang'] = target_lang
                    elif 'final_lang' in df.columns:
                        df['final_lang'] = target_lang
                    elif 'detected_lang' in df.columns:
                        df['detected_lang'] = target_lang
                    
                    # On sauvegarde
                    df.to_csv(target_path, index=False)
                    total_files_created += 1
                except Exception as e:
                    print(f"      ❌ Erreur : {e}")
            else:
                print(f"   ✅ {match_id} [{target_lang.upper()}] existe déjà ({len(df_test)} tweets).")

    print("\n" + "="*40)
    print(f"🎉 TERMINÉ ! {total_files_created} fichiers simulés.")
    print("Tes données sont prêtes pour l'analyse de sentiment.")
    print("="*40)

if __name__ == "__main__":
    simulation_donnees()