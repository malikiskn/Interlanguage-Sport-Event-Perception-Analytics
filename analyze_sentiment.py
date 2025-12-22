from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
import torch
import pandas as pd
import os
import glob
import numpy as np

# --- CONFIGURATION ---
DATA_DIR = "collect_data/data"
RESULTS_DIR = "results"
# Modèle célèbre entraîné sur ~124 millions de tweets (le standard académique)
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

def preprocess_tweet(text):
    """Nettoie le tweet pour que l'IA le comprenne mieux."""
    if not isinstance(text, str):
        return ""
    new_text = []
    for t in text.split(" "):
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)

def run_analysis():
    print(f"🧠 Chargement du modèle IA '{MODEL_NAME}' sur le Mac M4...")
    
    # 1. Chargement du Tokenizer (le traducteur Texte -> Chiffres) et du Modèle
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    
    # Création du dossier de résultats
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    # Récupération des fichiers
    files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    print(f"📂 {len(files)} fichiers trouvés à analyser.")

    # Labels du modèle
    labels = ['Negative', 'Neutral', 'Positive']

    for i, file_path in enumerate(files):
        filename = os.path.basename(file_path)
        print(f"\n[{i+1}/{len(files)}] Analyse de : {filename} ...")
        
        try:
            df = pd.read_csv(file_path)
            
            # On vérifie que le fichier n'est pas vide
            if len(df) == 0:
                print("   ⚠️ Fichier vide, on passe.")
                continue

            # Création des listes pour stocker les résultats
            sentiment_results = []
            confidence_scores = []

            # BOUCLE SUR CHAQUE TWEET (C'est là que l'IA travaille)
            # On prend un échantillon si c'est trop gros pour aller vite ce soir
            tweets_to_process = df['tweet_text'].tolist()
            
            for tweet in tweets_to_process:
                # A. Nettoyage
                clean_text = preprocess_tweet(tweet)
                
                # B. Transformation en chiffres (Tensors)
                encoded_input = tokenizer(clean_text, return_tensors='pt')
                
                # C. Prédiction (Le cerveau réfléchit)
                with torch.no_grad(): # On désactive l'apprentissage pour aller plus vite
                    output = model(**encoded_input)
                
                # D. Calcul des scores (Probabilités)
                scores = output[0][0].detach().numpy()
                scores = softmax(scores) # Transforme en % (ex: 0.9, 0.05, 0.05)
                
                # E. Décision
                ranking = np.argsort(scores)
                top_ranking = ranking[-1] # Le score le plus élevé
                
                sentiment = labels[top_ranking]
                confidence = scores[top_ranking]
                
                sentiment_results.append(sentiment)
                confidence_scores.append(confidence)

            # Ajout des colonnes au fichier Excel/CSV
            df['ai_sentiment'] = sentiment_results
            df['ai_score'] = confidence_scores
            
            # Sauvegarde dans le nouveau dossier
            output_path = os.path.join(RESULTS_DIR, f"analyzed_{filename}")
            df.to_csv(output_path, index=False)
            print(f"   ✅ Sauvegardé dans : {output_path}")

        except Exception as e:
            print(f"   ❌ Erreur sur ce fichier : {e}")

    print("\n" + "="*50)
    print("🚀 TERMINÉ ! Tous les tweets ont été analysés par l'IA.")
    print(f"👉 Va voir dans le dossier '{RESULTS_DIR}' pour les résultats.")
    print("="*50)

if __name__ == "__main__":
    run_analysis()