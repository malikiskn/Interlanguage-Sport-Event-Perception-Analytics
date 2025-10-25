"""Configuration helpers for Champions League match data collection."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class QueryConfig:
    """Description of a search query for a specific language."""

    language: str
    query: str
    max_tweets: int = 500
    additional_params: Optional[dict] = None


@dataclass
class MatchConfig:
    """Stores metadata for a single match collection campaign."""

    match_id: str
    home_team: str
    away_team: str
    competition: str
    start_time: str
    end_time: str
    queries: List[QueryConfig] = field(default_factory=list)
    notes: Optional[str] = None


DEFAULT_MATCHES: List[MatchConfig] = [
    MatchConfig(
    match_id="2025-10-21_arsenal_atletico",
    home_team="Arsenal FC",
    away_team="Atlético Madrid",
    competition="UEFA Champions League",  
    start_time="2025-10-21T22:00:00Z",   # 21h00 heure de Paris
    end_time="2025-10-21T23:00:00Z",     # ≈ 2 heures après la fin du match
    notes=(
        "Match joué à 21h00 heure de Paris (UTC+2). "
        "Fenêtre de collecte couvrant la durée du match et les 2 heures post-match."
    ),
    queries=[
        QueryConfig(
            language="en",
            query="(#ARSMAD OR #AFCATL OR #UCL OR #ChampionsLeague OR "
                  "Arsenal OR Gunners OR Atletico) lang:en",
            max_tweets=5,
        ),
        QueryConfig(
            language="es",
            query="(#ARSMAD OR #AFCATL OR #UCL OR #LDC OR Arsenal OR Atletico) lang:fr",
            max_tweets=10,
        ),
        QueryConfig(
            language="fr",
            query="(#ARSMAD OR #AFCATL OR #UCL OR #ChampionsLeague OR Arsenal OR Atletico) lang:es",
            max_tweets=10,
        ),
    ],
)
]
  

def get_match_by_id(match_id: str) -> Optional[MatchConfig]:
    """Retrieve a match configuration by its identifier."""

    return next((match for match in DEFAULT_MATCHES if match.match_id == match_id), None)
