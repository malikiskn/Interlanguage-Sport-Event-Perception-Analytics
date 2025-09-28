"""Tools to download Champions League reactions from X (Twitter)."""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

from .match_config import DEFAULT_MATCHES, MatchConfig, QueryConfig, get_match_by_id
from .twitter_client import TwitterAPIError, TwitterClient


def load_bearer_token(env_path: Optional[str] = None) -> str:
    """Return the bearer token from the environment or a .env file."""

    token = os.getenv("TWITTER_BEARER_TOKEN")
    if token:
        return token

    if env_path:
        path = Path(env_path)
        if path.exists():
            with path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("TWITTER_BEARER_TOKEN="):
                        return line.split("=", 1)[1].strip().strip('"')

    raise RuntimeError(
        "Cannot find TWITTER_BEARER_TOKEN. Export it or add it to the .env file."
    )


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect Champions League supporter reactions from X (Twitter)."
    )
    parser.add_argument(
        "--match-id",
        action="append",
        help=(
            "Identifier(s) of the matches to collect. "
            "Defaults to all matches defined in match_config.py"
        ),
    )
    parser.add_argument(
        "--output-dir",
        default="collect_data/data",
        help="Directory where JSONL files will be stored.",
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to the .env file containing the TWITTER_BEARER_TOKEN variable.",
    )
    parser.add_argument(
        "--max-per-query",
        type=int,
        help="Override the per-query tweet limit defined in match_config.py",
    )
    parser.add_argument(
        "--language",
        "--lang",
        dest="languages",
        action="append",
        help=(
            "Collect only queries matching the specified language code. "
            "Repeat the option to include multiple languages (e.g. --lang fr --lang en)."
        ),
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=1.0,
        help="Seconds to sleep between paginated requests to avoid rate limits.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Load configuration and authenticate but do not call the API.",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append to existing JSONL files instead of overwriting them.",
    )
    return parser.parse_args(argv)


def select_matches(match_ids: Optional[Iterable[str]]) -> Iterable[MatchConfig]:
    if not match_ids:
        return DEFAULT_MATCHES

    matches: list[MatchConfig] = []
    for match_id in match_ids:
        match = get_match_by_id(match_id)
        if match is None:
            raise SystemExit(f"Match '{match_id}' not found in match_config.py")
        matches.append(match)
    return matches


def collect_query(
    client: TwitterClient,
    match: MatchConfig,
    query_config: QueryConfig,
    *,
    output_file: Path,
    sleep_seconds: float,
    append: bool,
    max_per_query: Optional[int] = None,
) -> int:
    """Fetch tweets for a single query and persist them to disk."""

    effective_limit = min(max_per_query, query_config.max_tweets) if max_per_query else query_config.max_tweets
    if effective_limit <= 0:
        return 0

    output_file.parent.mkdir(parents=True, exist_ok=True)

    mode = "a" if append and output_file.exists() else "w"
    if mode == "w" and output_file.exists():
        output_file.unlink()

    total_written = 0
    next_token: Optional[str] = None
    request_count = 0

    with output_file.open(mode, encoding="utf-8") as handle:
        while total_written < effective_limit:
            batch_size = min(100, effective_limit - total_written)
            payload = client.search_recent(
                query=query_config.query,
                start_time=match.start_time,
                end_time=match.end_time,
                next_token=next_token,
                max_results=batch_size,
                additional_params=query_config.additional_params,
            )
            request_count += 1
            tweets = payload.get("data", [])
            includes = payload.get("includes", {})
            if not tweets:
                break

            user_map = {u["id"]: u for u in includes.get("users", [])}
            timestamp = datetime.now(timezone.utc).isoformat()

            for tweet in tweets:
                author = user_map.get(tweet.get("author_id"))
                record = {
                    "collected_at": timestamp,
                    "match_id": match.match_id,
                    "competition": match.competition,
                    "home_team": match.home_team,
                    "away_team": match.away_team,
                    "query": query_config.query,
                    "query_language": query_config.language,
                    "tweet": tweet,
                    "author": author,
                }
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                total_written += 1

            next_token = payload.get("meta", {}).get("next_token")
            if not next_token:
                break
            time.sleep(max(0.0, sleep_seconds))

    print(
        f"  - {query_config.language}: stored {total_written} tweets "
        f"in {output_file.name} (requests: {request_count})"
    )
    return total_written


def main(argv: Optional[Iterable[str]] = None) -> None:
    args = parse_args(argv)
    bearer_token = load_bearer_token(args.env_file)
    matches = list(select_matches(args.match_id))
    languages = set(args.languages) if args.languages else None

    if args.dry_run:
        print(f"Dry run successful. Loaded {len(matches)} match configuration(s).")
        if languages:
            print(f"Language filter: {sorted(languages)}")
        return

    client = TwitterClient(bearer_token=bearer_token)
    total = 0

    for match in matches:
        print(f"Collecting match {match.match_id} ({match.home_team} vs {match.away_team})")
        filtered_queries = [
            query_config for query_config in match.queries
            if not languages or query_config.language in languages
        ]
        if not filtered_queries:
            print(
                f"  ! No queries matching languages {sorted(languages)} for this match."
            )
            continue

        for query_config in filtered_queries:
            output_filename = f"{match.match_id}_{query_config.language}.jsonl"
            output_path = Path(args.output_dir) / output_filename
            written = collect_query(
                client,
                match,
                query_config,
                output_file=output_path,
                sleep_seconds=args.sleep,
                append=args.append,
                max_per_query=args.max_per_query,
            )
            total += written

    print(f"Done. Stored {total} tweets across {len(matches)} match(es).")


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except TwitterAPIError as exc:
        raise SystemExit(f"Request to X API failed: {exc}")
