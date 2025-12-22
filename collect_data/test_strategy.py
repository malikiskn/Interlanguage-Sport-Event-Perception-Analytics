import pandas as pd
from ntscraper import Nitter
import time
import random

def collecter_match_readme(match_name, query_base, date_start, date_end, lang_A, lang_B, lang_Neutral):
    """
    Collecte les tweets selon la stratégie du README : ~167 tweets par langue.
    """
    scraper = Nitter(log_level=1, skip_instance_check=True)
    all_data = []
    
    # Configuration des 3 langues cibles (Partisane A, Partisane B, Neutre)
    # On met 180 pour avoir une marge de sécurité et atteindre les 167 après nettoyage
    targets = [
        {"lang": lang_A, "count": 180, "role": "Partisan A"},
        {"lang": lang_B, "count": 180, "role": "Partisan B"},
        {"lang": lang_Neutral, "count": 180, "role": "Neutre (Third-party)"}
    ]
    
    print(f"🏟️  DÉBUT COLLECTE: {match_name}")
    print(f"📅  Période : {date_start} au {date_end}")

    for target in targets:
        lang = target['lang']
        count = target['count']
        role = target['role']
        
        # Construction de la requête précise
        full_query = f"{query_base} lang:{lang} since:{date_start} until:{date_end}"
        print(f"\n   Downloading {role} ({lang})... Objectif: {count}")
        
        try:
            # Appel au Scraper
            tweets = scraper.get_tweets(full_query, mode='term', number=count)
            
            if 'tweets' in tweets and len(tweets['tweets']) > 0:
                found = len(tweets['tweets'])
                print(f"   ✅ Trouvé : {found} tweets")
                
                for t in tweets['tweets']:
                    all_data.append({
                        'match': match_name,
                        'role': role,
                        'lang': lang,
                        'text': t['text'],
                        'date': t['date'],
                        'likes': t['stats']['likes'],
                        'retweets': t['stats']['retweets'],
                        'user': t['user']['username'],
                        'tweet_url': t['link']
                    })
            else:
                print(f"   ⚠️ Zéro tweet trouvé pour {lang}. (Instance bloquée ou pas de data)")
                
        except Exception as e:
            print(f"   ❌ Erreur technique sur {lang}: {e}")
        
        # Petite pause aléatoire pour ne pas se faire bloquer
        time.sleep(random.uniform(2, 5))

    return all_data

# --- CONFIGURATION DU TEST (Exemple: PSG vs Dortmund - Décembre 2023) ---
# Ce match est parfait pour tester : FR vs DE, avec EN en neutre.

DATA = collecter_match_readme(
    match_name="2023-12-13_Dortmund_PSG",
    query_base="#BVBPSG OR #PSGBVB OR Dortmund OR PSG OR Mbappe", # Mots clés
    date_start="2023-12-13", # Jour J
    date_end="2023-12-15",   # J+2
    lang_A="fr",             # Français (Partisan A)
    lang_B="de",             # Allemand (Partisan B)
    lang_Neutral="en"        # Anglais (Neutre)
)

# --- SAUVEGARDE ---
if DATA:
    df = pd.DataFrame(DATA)
    print("\n" + "="*30)
    print(f"🎉 RÉSULTAT FINAL : {len(df)} tweets collectés")
    print("Répartition :")
    print(df['lang'].value_counts())
    
    filename = "test_readme_strategy.csv"
    df.to_csv(filename, index=False)
    print(f"💾 Sauvegardé dans {filename}")
else:
    print("\n❌ Aucun tweet récupéré. Réessayez, les serveurs Nitter sont parfois capricieux.")