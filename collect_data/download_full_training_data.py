from datasets import load_dataset
import pandas as pd
import os
import time

def download_and_merge_full_dataset():
    # Liste des langues
    languages = ['english', 'french', 'spanish', 'german', 'italian', 'portuguese']
    
    lang_map = {
        'english': 'en', 'french': 'fr', 'spanish': 'es', 
        'german': 'de', 'italian': 'it', 'portuguese': 'pt'
    }

    output_dir = 'collect_data/data/training_data'
    os.makedirs(output_dir, exist_ok=True)
    
    all_tweets = []
    
    print("🚀 Démarrage du téléchargement MASSIF (CardiffNLP)...")

    for lang_name in languages:
        print(f"\n🌍 Traitement de la langue : {lang_name}...")
        try:
            # On charge TOUT (train, test, validation)
            # trust_remote_code=True est nécessaire pour la version 2.19.0 que tu as installée
            dataset = load_dataset(
                "cardiffnlp/tweet_sentiment_multilingual", 
                lang_name, 
                trust_remote_code=True
            )
            
            # On récupère les 3 parties
            splits = ['train', 'validation', 'test']
            
            for split in splits:
                if split in dataset:
                    df = pd.DataFrame(dataset[split])
                    
                    # Nettoyage et Standardisation
                    df['lang'] = lang_map[lang_name]
                    df = df.rename(columns={'label': 'sentiment_score'})
                    
                    # On ajoute à la liste globale
                    all_tweets.append(df)
                    print(f"   ✅ {split.upper()} ajouté ({len(df)} tweets)")
                    
        except Exception as e:
            print(f"   ⚠️ Erreur pour {lang_name}: {e}")
            time.sleep(2)

    # FUSION FINALE
    if all_tweets:
        print("\n🌪️ Fusion de toutes les langues en un seul fichier...")
        full_df = pd.concat(all_tweets, ignore_index=True)
        
        # Mélanger les lignes pour que l'IA ne voit pas que du Français puis que de l'Anglais
        full_df = full_df.sample(frac=1).reset_index(drop=True)
        
        output_path = os.path.join(output_dir, "TRAINING_DATA_FULL_MULTILINGUAL.csv")
        full_df.to_csv(output_path, index=False)
        
        print(f"\n🎉 SUCCÈS TOTAL !")
        print(f"📦 Fichier créé : {output_path}")
        print(f"📊 Nombre total de tweets pour l'entraînement : {len(full_df)}")
        print("   (C'est parfait pour entraîner XLM-RoBERTa)")
    else:
        print("❌ Aucun tweet récupéré. Vérifie ta connexion.")

if __name__ == "__main__":
    download_and_merge_full_dataset()