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
        match_id="2024-10-01_psg_dortmund",
        home_team="Paris Saint-Germain",
        away_team="Borussia Dortmund",
        competition="UEFA Champions League",
        start_time="2024-10-01T19:00:00Z",
        end_time="2024-10-02T19:00:00Z",
        notes="Example configuration – update the time window around the actual fixture",
        queries=[
            QueryConfig(
                language="fr",
                query="(\"PSG\" OR \"Paris\") (\"Dortmund\" OR \"BVB\") lang:fr",
                max_tweets=600,
            ),
            QueryConfig(
                language="de",
                query="(\"Dortmund\" OR \"BVB\") (\"PSG\" OR \"Paris\") lang:de",
                max_tweets=600,
            ),
            QueryConfig(
                language="en",
                query="(#PSGBVB OR \"PSG\" OR \"Dortmund\") lang:en",
                max_tweets=400,
            ),
        ],
    ),
    MatchConfig(
        match_id="2024-10-02_real_barca",
        home_team="Real Madrid",
        away_team="FC Barcelona",
        competition="UEFA Champions League",
        start_time="2024-10-02T19:00:00Z",
        end_time="2024-10-03T19:00:00Z",
        notes="Second example – replace with the fixtures you plan to analyse",
        queries=[
            QueryConfig(
                language="es",
                query="(\"Real Madrid\" OR \"Hala Madrid\") (\"Barcelona\" OR \"Barça\") lang:es",
            ),
            QueryConfig(
                language="en",
                query="(\"Real Madrid\" OR \"Barcelona\") (#UCL OR \"Champions League\") lang:en",
                max_tweets=300,
            ),
            QueryConfig(
                language="ca",
                query="(\"Barça\" OR \"Barcelona\") (\"Madrid\") lang:ca",
                max_tweets=200,
            ),
        ],
    ),
    MatchConfig(
        match_id="2025-09-28_newcastle_arsenal",
        home_team="Newcastle United",
        away_team="Arsenal FC",
        competition="Premier League",
        start_time="2025-09-28T15:30:00Z",
        end_time="2025-09-28T20:45:00Z",
        notes="Match joué à 17h30 heure de Paris (UTC+2). Ajustez la fenêtre selon le volume désiré.",
        queries=[
            QueryConfig(
                language="en",
                query="(#NEWARS OR #NUFC OR #AFC OR Newcastle OR Arsenal) lang:en",
                max_tweets=10,
            ),
            QueryConfig(
                language="fr",
                query="(#NEWARS OR Newcastle OR Arsenal) lang:fr",
                max_tweets=10,
            ),
        ],
    ),
]


def get_match_by_id(match_id: str) -> Optional[MatchConfig]:
    """Retrieve a match configuration by its identifier."""

    return next((match for match in DEFAULT_MATCHES if match.match_id == match_id), None)
