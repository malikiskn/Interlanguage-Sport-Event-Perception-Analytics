"""Configuration for World Cup 2018 data collection."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class QueryConfig:
    language: str
    query: str
    max_tweets: int = 500 # Pas utilisé pour le filtrage CSV local, mais requis par le code
    additional_params: Optional[dict] = None

@dataclass
class MatchConfig:
    match_id: str
    home_team: str
    away_team: str
    competition: str
    start_time: str
    end_time: str
    queries: List[QueryConfig] = field(default_factory=list)
    notes: Optional[str] = None

# --- LISTE DES CONFIGURATIONS ---
DEFAULT_MATCHES: List[MatchConfig] = [
    MatchConfig(
        # On donne un nom générique pour créer un dossier qui contiendra tout
        match_id="world_cup_2018_global", 
        home_team="World",
        away_team="Cup",
        competition="FIFA World Cup 2018",
        
        # Période large : Du début à la fin de la coupe du monde (Juin - Juillet 2018)
        start_time="2018-06-14T00:00:00Z", 
        end_time="2018-07-16T23:59:00Z",
        
        queries=[
            # ANGLAIS
            QueryConfig(language="en", query="WorldCup OR #WorldCup2018 OR FIFA OR Football OR Soccer"),
            # FRANÇAIS
            QueryConfig(language="fr", query="CoupeDuMonde OR #CM2018 OR Mondial OR Football"),
            # ESPAGNOL
            QueryConfig(language="es", query="CopaMundial OR #Rusia2018 OR Futbol"),
            # ALLEMAND
            QueryConfig(language="de", query="Weltmeisterschaft OR #WM2018 OR Fussball"),
            # ITALIEN
            QueryConfig(language="it", query="CoppaDelMondo OR #Mondiali2018 OR Calcio"),
            # PORTUGAIS
            QueryConfig(language="pt", query="CopaDoMundo OR #Copa2018 OR Futebol"),
        ],
    )
]

def get_match_by_id(match_id: str) -> Optional[MatchConfig]:
    return next((match for match in DEFAULT_MATCHES if match.match_id == match_id), None)

# --- LE PONT (Transformation pour ton script) ---
MATCHES = {}

for m in DEFAULT_MATCHES:
    simple_keywords = []
    available_languages = []

    for q in m.queries:
        available_languages.append(q.language)
        # Nettoyage des mots-clés
        raw = q.query.replace('(', '').replace(')', '').replace('"', '')
        terms = raw.split(' OR ')
        for t in terms:
            clean_term = t.split(' ')[0].strip()
            if clean_term and not clean_term.startswith('lang:'):
                simple_keywords.append(clean_term)
    
    # On ajoute des mots-clés génériques pour être sûr de tout attraper
    simple_keywords.extend(["FIFA", "WorldCup", "2018", "Football", "Soccer", "Messi", "Ronaldo", "Mbappe", "Neymar"])
    
    MATCHES[m.match_id] = {
        "keywords": list(set(simple_keywords)), 
        "languages": list(set(available_languages)),
        "start_time": m.start_time,
        "end_time": m.end_time,
        "home_team": m.home_team,
        "away_team": m.away_team,
        "competition": m.competition
    }