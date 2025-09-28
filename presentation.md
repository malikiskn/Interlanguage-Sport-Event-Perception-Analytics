# 🏆 Projet de Recherche : Analyse des Sentiments Multilingues après les Matchs de Football

## 📋 Résumé Exécutif

Ce projet de recherche vise à analyser les réactions des supporters de football dans différentes langues après les matchs de Ligue des Champions, en étudiant les biais cognitifs liés à la victoire ou à la défaite de leur équipe.

## 🎯 Objectifs du Projet

### Objectif Principal
Analyser les sentiments des supporters de football dans plusieurs langues après les matchs de Ligue des Champions pour comprendre les biais cognitifs liés aux résultats sportifs.

### Objectifs Spécifiques
1. **Collecte de données multilingues** : Récupérer les commentaires des supporters en français, allemand, anglais, espagnol et italien
2. **Analyse des biais** : Étudier comment la victoire/défaite influence la perception des supporters
3. **Classification automatique** : Développer un système pour identifier l'appartenance des supporters à une équipe
4. **Analyse comparative** : Comparer les réactions entre supporters gagnants et perdants

## 🔬 Contexte Scientifique

### Problématique de Recherche
Les supporters de football développent-ils des biais cognitifs différents selon le résultat de leur équipe ? Comment ces biais se manifestent-ils dans différentes langues et cultures ?

### Hypothèses
- **H1** : Les supporters de l'équipe gagnante ont tendance à légitimer le résultat même en cas d'erreurs arbitrales
- **H2** : Les supporters de l'équipe perdante ont tendance à contester le résultat et à critiquer l'arbitrage
- **H3** : Ces biais varient selon la langue et la culture des supporters

## 🌍 Portée Multilingue

### Langues Ciblées
- **Français** : Supporters du PSG, Monaco, etc.
- **Allemand** : Supporters du Bayern Munich, Borussia Dortmund, etc.
- **Anglais** : Supporters des clubs anglais (Arsenal, Manchester City, etc.)
- **Espagnol** : Supporters du Real Madrid, Barcelone, etc.
- **Italien** : Supporters de la Juventus, AC Milan, Inter, etc.

### Stratégie de Collecte
- **Matchs internationaux** : Privilégier les confrontations entre clubs de différents pays
- **Langue neutre** : Utiliser l'anglais comme langue de référence
- **Période d'analyse** : 24 heures après chaque match

## 🛠️ Méthodologie Technique

### 1. Collecte de Données
- **Source** : X (twitter) (r/soccer, r/championsleague, r/football)
- **Type de données** : Commentaires des posts de match
- **Volume cible** : 500 commentaires par match, 20 matchs minimum
- **Période** : Saison 2024-2025 de Ligue des Champions

### 2. Traitement des Données
- **Détection de langue** : Utilisation de `langdetect` pour identifier automatiquement la langue
- **Classification d'équipe** : Règles basées sur des mots-clés et l'analyse du contexte
- **Nettoyage** : Suppression des commentaires trop courts ou non pertinents

### 3. Analyse des Sentiments
- **Modèles pré-entraînés** : Utilisation de `transformers` pour l'analyse multilingue
- **Métriques** : Positivité, négativité, neutralité
- **Classification** : Sentiment global et sentiment par aspect (arbitrage, performance, etc.)

### 4. Analyse des Biais
- **Comparaison gagnant/perdant** : Analyse comparative des sentiments
- **Analyse temporelle** : Évolution des sentiments dans le temps
- **Analyse culturelle** : Comparaison entre différentes langues/cultures

## 📊 Structure des Données

### Base de Données
- **Table `matches`** : Informations sur les matchs (équipes, date, score, etc.)
- **Table `comments`** : Commentaires des supporters avec métadonnées
- **Table `sentiments`** : Résultats de l'analyse des sentiments
- **Table `biases`** : Analyse des biais par match et par équipe

### Métadonnées Collectées
- **Commentaire** : Contenu textuel
- **Auteur** : Nom d'utilisateur X (twitter)
- **Date** : Timestamp de création
- **Score** : Score X (twitter) (upvotes/downvotes)
- **Langue détectée** : Langue automatiquement identifiée
- **Équipe identifiée** : Équipe supportée (si identifiable)

## 🔍 Exemples d'Analyse

### Cas d'Étude : PSG vs Borussia Dortmund
- **Date** : 2025-09-12
- **Langues** : Français (PSG), Allemand (Dortmund), Anglais (neutre)
- **Analyse** : Comparaison des réactions des supporters selon le résultat

### Métriques d'Analyse
- **Sentiment moyen** par équipe et par langue
- **Distribution des sentiments** (positif/négatif/neutre)
- **Mots-clés** les plus fréquents par sentiment
- **Évolution temporelle** des sentiments

## 🎯 Applications et Impact

### Applications Académiques
- **Psychologie sociale** : Compréhension des biais cognitifs
- **Linguistique** : Analyse des expressions émotionnelles multilingues
- **Sciences du sport** : Impact psychologique des résultats sportifs

### Applications Pratiques
- **Médias sportifs** : Compréhension des réactions des supporters
- **Clubs de football** : Analyse de la perception des supporters
- **Arbitrage** : Compréhension de la perception des décisions arbitrales

## 🚀 Développement Technique

### Architecture du Système
```
ProjetRecherche/
├── match_config.py          # Configuration des matchs
├── match_database.py        # Gestion de la base de données
├── match_collector.py       # Collecteur de commentaires
├── view_match_data.py       # Visualisation des données
├── champions_league_comments.db  # Base de données
└── requirements_simple.txt  # Dépendances
```

### Technologies Utilisées
- **Python 3.8+** : Langage de programmation principal
- **X (twitter) API (PRAW)** : Collecte de données
- **SQLite** : Base de données locale
- **Pandas** : Manipulation des données
- **Transformers** : Analyse des sentiments
- **LangDetect** : Détection de langue

## 📈 Résultats Attendus

### Données Collectées
- **20+ matchs** de Ligue des Champions
- **10,000+ commentaires** multilingues
- **5 langues** différentes
- **Analyse temporelle** sur 24h post-match

### Insights Attendus
1. **Identification des biais** : Confirmation des hypothèses sur les biais cognitifs
2. **Différences culturelles** : Variation des réactions selon la langue/culture
3. **Patterns temporels** : Évolution des sentiments dans le temps
4. **Facteurs d'influence** : Impact du score, de l'arbitrage, etc.

## 🔮 Perspectives d'Évolution

### Phase 1 (Actuelle)
- Collecte de données brutes
- Détection de langue basique
- Classification d'équipe simple

### Phase 2 (Future)
- Analyse des sentiments avancée
- Classification automatique des supporters
- Analyse des biais cognitifs

### Phase 3 (Avancée)
- Modèles de prédiction
- Interface web interactive
- Publication des résultats

## 📚 Bibliographie et Références

### Articles Scientifiques
- "Cognitive Biases in Sports: A Review" (2023)
- "Multilingual Sentiment Analysis: Challenges and Opportunities" (2024)
- "Social Media and Sports: Psychological Perspectives" (2023)

### Outils et Technologies
- X (twitter) API Documentation
- Transformers Library (Hugging Face)
- LangDetect Library
- PRAW (Python X (twitter) API Wrapper)

## 🎓 Contribution Académique

### Objectifs de Publication
- **Conférence** : International Conference on Sports Analytics
- **Journal** : Journal of Sports Psychology
- **Thèse** : Contribution à la thèse de Master 2

### Valeur Ajoutée
- **Nouveauté** : Première analyse multilingue des biais cognitifs en football
- **Méthodologie** : Approche innovante combinant NLP et psychologie sociale
- **Données** : Dataset unique de commentaires multilingues

## 📞 Contact et Collaboration

### Équipe de Recherche
- **Étudiant** : Mamoudou [Nom de famille]
- **Institution** : Université de Caen Normandie
- **Programme** : Master 2 Recherche
- **Superviseur** : [Nom du superviseur]

### Partenaires Potentiels
- Clubs de football (PSG, Borussia Dortmund, etc.)
- Médias sportifs (L'Équipe, Kicker, etc.)
- Laboratoires de recherche en psychologie sociale

---

*Ce projet s'inscrit dans le cadre d'un Master 2 Recherche en Sciences du Sport et vise à contribuer à la compréhension des biais cognitifs dans le sport professionnel.*
