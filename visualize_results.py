import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os

# --- CONFIGURATION ---
RESULTS_DIR = "results"
CHARTS_DIR = "charts"

# Création du dossier pour les images
os.makedirs(CHARTS_DIR, exist_ok=True)

def generate_graphs():
    print("🎨 Génération des graphiques en cours...")
    
    all_files = glob.glob(os.path.join(RESULTS_DIR, "*.csv"))
    
    if not all_files:
        print("❌ Aucun fichier de résultats trouvé !")
        return

    # 1. On fusionne tous les résultats en un seul gros tableau
    li = []
    for filename in all_files:
        df = pd.read_csv(filename)
        # On extrait la langue et le match depuis le nom du fichier
        # Ex: analyzed_2022-12-18_france_argentina_en.csv
        name_parts = os.path.basename(filename).replace("analyzed_", "").replace(".csv", "").split("_")
        lang = name_parts[-1] # La dernière partie est la langue (en, fr, es...)
        match_name = "_".join(name_parts[1:-1]) # Le reste est le nom du match
        
        df['Language'] = lang
        df['Match'] = match_name
        li.append(df)

    big_df = pd.concat(li, axis=0, ignore_index=True)
    
    print(f"📊 Données chargées : {len(big_df)} tweets analysés.")

    # --- GRAPHIQUE 1 : Sentiment Global (Camembert) ---
    plt.figure(figsize=(8, 8))
    colors = {'Negative': '#ff9999', 'Neutral': '#66b3ff', 'Positive': '#99ff99'}
    
    sentiment_counts = big_df['ai_sentiment'].value_counts()
    plt.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', startangle=140, colors=[colors[k] for k in sentiment_counts.index])
    plt.title('Distribution Globale des Sentiments (Coupe du Monde)')
    
    save_path = os.path.join(CHARTS_DIR, "global_sentiment_pie.png")
    plt.savefig(save_path)
    print(f"   ✅ Graphique sauvé : {save_path}")
    plt.close()

    # --- GRAPHIQUE 2 : Sentiment par Match (Barres Empilées) ---
    plt.figure(figsize=(12, 6))
    
    # On croise les données : Pour chaque match, combien de Pos/Neg/Neu ?
    cross_tab = pd.crosstab(big_df['Match'], big_df['ai_sentiment'], normalize='index') * 100
    
    # On trie pour avoir les matchs les plus "Négatifs" en premier (intéressant pour l'analyse)
    if 'Negative' in cross_tab.columns:
        cross_tab = cross_tab.sort_values('Negative', ascending=False)
    
    cross_tab.plot(kind='bar', stacked=True, color=[colors.get(x, '#333') for x in cross_tab.columns], figsize=(12,8))
    
    plt.title('Sentiment par Match (Pourcentage)')
    plt.ylabel('Pourcentage')
    plt.xlabel('Match')
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Sentiment')
    plt.tight_layout()
    
    save_path = os.path.join(CHARTS_DIR, "sentiment_by_match.png")
    plt.savefig(save_path)
    print(f"   ✅ Graphique sauvé : {save_path}")
    plt.close()

    # --- GRAPHIQUE 3 : Comparaison par Langue (Barres) ---
    plt.figure(figsize=(10, 6))
    sns.countplot(data=big_df, x='Language', hue='ai_sentiment', palette=colors)
    plt.title('Comparaison des Sentiments par Langue')
    plt.xlabel('Langue')
    plt.ylabel('Nombre de Tweets')
    
    save_path = os.path.join(CHARTS_DIR, "sentiment_by_language.png")
    plt.savefig(save_path)
    print(f"   ✅ Graphique sauvé : {save_path}")
    plt.close()

    print("\n🚀 TERMINÉ ! Tes graphiques sont dans le dossier 'charts'.")

if __name__ == "__main__":
    generate_graphs()