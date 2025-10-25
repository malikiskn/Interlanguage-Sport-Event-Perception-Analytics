# Collecte des données X (Twitter)

Ce module permet de récupérer les réactions des supporters après les matchs de Ligue des Champions afin de constituer un jeu de données multilingue.

## Pré-requis

- Python 3.10+
- Bibliothèque `requests` (installée par défaut dans la plupart des environnements)
- Variable d'environnement `TWITTER_BEARER_TOKEN` configurée (ou présente dans `.env`)

## Configuration des matchs

Modifiez `collect_data/match_config.py` pour lister les rencontres à suivre. Chaque entrée définit :
- un identifiant `match_id`
- la fenêtre temporelle (`start_time`, `end_time`) au format ISO 8601 UTC
- les requêtes multilingues associées (champ `query` utilise la syntaxe opérateurs de l'API X)

> Astuce : commencez avec une fenêtre de 6 à 12 heures autour du match, puis élargissez selon le volume obtenu.

## Lancer une premiere collecte

```bash
python -m collect_data.collector --match-id 2025-09-28_newcastle_arsenal --lang fr
```

## Lancer une autre collecte

```bash
python -m collect_data.collector --match-id 2025-09-28_newcastle_arsenal --lang fr --append
```

Paramètres utiles :

- `--output-dir collect_data/data` : dossier de sortie (CSV)
- `--max-per-query 400` : limite le nombre de tweets par requête
- `--lang fr --lang en` : filtre les requêtes sur une ou plusieurs langues configurées
- `--sleep 1.5` : pause entre deux appels pour éviter les limitations de taux
- `--append` : ajoute les nouvelles lignes en conservant le fichier CSV existant
- `--dry-run` : vérifie l'authentification et la configuration sans appeler l'API

Chaque ligne CSV contient :
- les métadonnées du match et de la requête (`match_id`, langue, etc.)
- les informations principales du tweet (texte, langue, métriques publiques)
- des attributs auteur (identifiant, nom, compte vérifié, followers, ...)

## Bonnes pratiques

- Surveillez les limites de l'API X (`HTTP 429`). Augmentez `--sleep` si nécessaire.
- Ajustez les requêtes pour capter la terminologie propre à chaque langue (hashtags, surnoms, acronymes).
- Dupliquez les requêtes pour couvrir les conversations neutres (anglais) et les discussions partisanes (langues locales).
- Documentez la date et l'heure de chaque collecte pour faciliter les analyses temporelles.

## Organisation des données

Les fichiers produits suivent la convention :

```
collect_data/data/<match_id>_<langue>.csv
```

Vous pouvez ensuite charger ces fichiers avec `pandas.read_csv` ou les importer dans SQLite pour la suite du projet.


## Principales langues: 
italien : it
espagnol : es
anglais : en
allemand : de
français : fr

## Stratégie de Collecte Recommandée (Budget ~4000 Tweets)

Pour une analyse robuste dans le cadre d'un budget de collecte limité (environ 4000 tweets), voici une répartition équilibrée qui inclut les deux langues partisanes et une langue neutre pour chaque match.

| Catégorie | Recommandation (pour ~4000 tweets) | Total Partiel | Total Final |
| :--- | :--- | :--- | :--- |
| **Nombre total de matchs** | **8** | | **8 matchs** |
| **Tweets par match** | **500** | (8 matchs x 500) | **4000 tweets** |
| └── **Langue 1** (Partisane A) | ~167 | (8 matchs x 167) | ~1336 tweets |
| └── **Langue 2** (Partisane B) | ~167 | (8 matchs x 167) | ~1336 tweets |
| └── **Langue 3** (Neutre) | ~166 | (8 matchs x 166) | ~1328 tweets |

Cette approche privilégie un nombre d'échantillons suffisant par groupe linguistique tout en couvrant plusieurs matchs pour assurer la généralisabilité des résultats.
