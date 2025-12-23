import os

# --- 🛑 ZONE DE SÉCURITÉ OBLIGATOIRE (M4) ---
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
# --------------------------------------------

import pandas as pd
import glob
import torch
import numpy as np
# 👇 CHANGEMENT ICI : On importe directement la classe RoBERTa
from transformers import AutoTokenizer, RobertaForSequenceClassification
from scipy.special import softmax

# --- CONFIGURATION ---
DATA_DIR = "collect_data/data"
RESULTS_DIR = "results"
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

def preprocess_tweet(text):
    if not isinstance(text, str): return ""
    new_text = []
    for t in text.split(" "):
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)

def run_analysis():
    print(f"🧠 Chargement du modèle sur Mac M4 (Mode Force)...")
    
    # 1. Chargement Tokenizer & Modèle (Avec classe explicite)
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        # 👇 CHANGEMENT ICI : On force l'utilisation de RoBERTa
        model = RobertaForSequenceClassification.from_pretrained(MODEL_NAME)
    except Exception as e:
        print(f"❌ Erreur critique : {e}")
        return

    os.makedirs(RESULTS_DIR, exist_ok=True)
    files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    labels = ['Negative', 'Neutral', 'Positive']

    print(f"📂 {len(files)} fichiers trouvés.")

    for i, file_path in enumerate(files):
        filename = os.path.basename(file_path)
        print(f"[{i+1}/{len(files)}] Traitement : {filename}")
        
        try:
            df = pd.read_csv(file_path)
            if len(df) == 0: continue

            texts = df['tweet_text'].tolist()
            # On ne traite que les 50 premiers pour tester si ça passe (optionnel)
            # texts = texts[:50] 
            
            processed_texts = [preprocess_tweet(t) for t in texts]
            
            sentiments = []
            scores_list = []

            # Analyse ligne par ligne
            for text in processed_texts:
                encoded = tokenizer(text, return_tensors='pt')
                output = model(**encoded)
                scores = output[0][0].detach().numpy()
                scores = softmax(scores)
                
                ranking = np.argsort(scores)
                top_rank = ranking[-1]
                
                sentiments.append(labels[top_rank])
                scores_list.append(scores[top_rank])

            df['ai_sentiment'] = sentiments
            df['ai_score'] = scores_list
            
            output_path = os.path.join(RESULTS_DIR, f"analyzed_{filename}")
            df.to_csv(output_path, index=False)
            print(f"   ✅ OK ({len(df)} tweets)")

        except Exception as e:
            print(f"   ⚠️ Erreur fichier : {e}")

    print("\n🚀 TERMINÉ ! Tout s'est bien passé.")

if __name__ == "__main__":
    run_analysis()