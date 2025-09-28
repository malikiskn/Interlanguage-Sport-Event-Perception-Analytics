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

## Lancer une collecte

```bash
python -m collect_data.collector --match-id 2025-09-28_newcastle_arsenal --lang fr
```

Paramètres utiles :

- `--output-dir collect_data/data` : dossier de sortie (JSON Lines)
- `--max-per-query 400` : limite le nombre de tweets par requête
- `--lang fr --lang en` : filtre les requêtes sur une ou plusieurs langues configurées
- `--sleep 1.5` : pause entre deux appels pour éviter les limitations de taux
- `--append` : ajoute les nouveaux tweets au fichier existant au lieu de l'écraser
- `--dry-run` : vérifie l'authentification et la configuration sans appeler l'API

Chaque fichier JSONL contient une ligne par tweet avec :
- le tweet complet (champ `tweet`)
- les informations auteur enrichies (`author`)
- les métadonnées du match et de la requête utilisée

## Bonnes pratiques

- Surveillez les limites de l'API X (`HTTP 429`). Augmentez `--sleep` si nécessaire.
- Ajustez les requêtes pour capter la terminologie propre à chaque langue (hashtags, surnoms, acronymes).
- Dupliquez les requêtes pour couvrir les conversations neutres (anglais) et les discussions partisanes (langues locales).
- Documentez la date et l'heure de chaque collecte pour faciliter les analyses temporelles.

## Organisation des données

Les fichiers produits suivent la convention :

```
collect_data/data/<match_id>_<langue>.jsonl
```

Vous pouvez ensuite charger ces fichiers avec `pandas` ou les ingérer dans SQLite pour la suite du projet.
