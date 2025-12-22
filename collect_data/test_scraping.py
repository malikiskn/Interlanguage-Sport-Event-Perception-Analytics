import pandas as pd
from ntscraper import Nitter
import time
import random
from datetime import datetime

# --- CONFIGURATION CIBLÉE (Juste un match pour tester) ---
MATCH = {
    "name": "2022_France_Argentina",
    "query": "France Argentina WorldCup", # Requete large
    "start": "2022-12-18",
    "end": "2022-12-19"
}

LANGUES = ["fr", "es", "en"] 
OBJECTIF = 50 # On commence petit pour voir si ça passe

def scraping_robuste():
    scraper = Nitter(log_level=1, skip_instance_check=True)
    results = []

    print(f"🐢 Démarrage du Scraping 'Mode Lent' pour {MATCH['name']}...")

    for lang in LANGUES:
        collected = 0
        attempt = 1
        
        while collected < OBJECTIF:
            try:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Tentative {attempt} pour la langue '{lang}'...")
                
                # Requete
                full_query = f"{MATCH['query']} lang:{lang} since:{MATCH['start']} until:{MATCH['end']}"
                
                # On demande par petits paquets de 20
                tweets = scraper.get_tweets(full_query, mode='term', number=20)
                
                if 'tweets' in tweets and len(tweets['tweets']) > 0:
                    new_tweets = tweets['tweets']
                    print(f"   ✅ Trouvé {len(new_tweets)} tweets !")
                    
                    for t in new_tweets:
                        results.append({
                            'lang': lang,
                            'text': t['text'],
                            'date': t['date'],
                            'user': t['user']['username']
                        })
                    
                    collected += len(new_tweets)
                    print(f"   💰 Total actuel pour {lang}: {collected}/{OBJECTIF}")
                else:
                    print("   ⚠️ Rien trouvé. Pause de 10s...")
                    time.sleep(10)

            except Exception as e:
                print(f"   ❌ Erreur : {e}")
                print("   💤 On attend 30 secondes avant de réessayer...")
                time.sleep(30)
            
            attempt += 1
            # Pause aléatoire pour ne pas ressembler à un robot
            time.sleep(random.uniform(5, 15))
            
            # Sécurité anti-boucle infinie (si vraiment ça marche pas au bout de 10 essais)
            if attempt > 10 and collected == 0:
                print("   ⛔ Abandon pour cette langue après 10 échecs.")
                break

    # Sauvegarde
    if results:
        df = pd.DataFrame(results)
        filename = f"scraping_lent_{MATCH['name']}.csv"
        df.to_csv(filename, index=False)
        print(f"\n🎉 Fini ! {len(df)} tweets sauvegardés dans {filename}")
    else:
        print("\n😭 Aucun tweet récupéré malgré les efforts.")

if __name__ == "__main__":
    scraping_robuste()