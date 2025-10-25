"""Tools to download Champions League reactions from X (Twitter)."""
from __future__ import annotations

import argparse
import csv
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

from .match_config import DEFAULT_MATCHES, MatchConfig, QueryConfig, get_match_by_id
from .twitter_client import TwitterAPIError, TwitterClient

CSV_FIELDS = [
    "collected_at",
    "match_id",
    "competition",
    "home_team",
    "away_team",
    "query",
    "query_language",
    "tweet_id",
    "tweet_created_at",
    "tweet_lang",
    "tweet_text",
    "conversation_id",
    "possibly_sensitive",
    "source",
    "retweet_count",
    "reply_count",
    "like_count",
    "quote_count",
    "author_id",
    "author_username",
    "author_name",
    "author_verified",
    "author_followers_count",
    "author_following_count",
    "author_tweet_count",
    "author_listed_count",
]


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
        help="Directory where CSV files will be stored.",
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
        "--since-id",
        type=str,
        help=(
            "Fetch only tweets newer than this tweet ID. "
            "Cannot be used with time filters (--no-time-filter will be auto-enabled)."
        ),
    )
    parser.add_argument(
        "--no-time-filter",
        action="store_true",
        help="Ignore start_time/end_time from match config. Useful with --since-id.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Load configuration and authenticate but do not call the API.",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append to existing CSV files instead of overwriting them.",
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


def build_row(
    *,
    timestamp: str,
    match: MatchConfig,
    query_config: QueryConfig,
    tweet: dict,
    author: Optional[dict],
) -> dict:
    """Convert the API payload to a flat CSV-friendly structure."""

    metrics = tweet.get("public_metrics") or {}
    author_metrics = (author or {}).get("public_metrics") or {}

    return {
        "collected_at": timestamp,
        "match_id": match.match_id,
        "competition": match.competition,
        "home_team": match.home_team,
        "away_team": match.away_team,
        "query": query_config.query,
        "query_language": query_config.language,
        "tweet_id": tweet.get("id"),
        "tweet_created_at": tweet.get("created_at"),
        "tweet_lang": tweet.get("lang"),
        "tweet_text": tweet.get("text"),
        "conversation_id": tweet.get("conversation_id"),
        "possibly_sensitive": tweet.get("possibly_sensitive"),
        "source": tweet.get("source"),
        "retweet_count": metrics.get("retweet_count"),
        "reply_count": metrics.get("reply_count"),
        "like_count": metrics.get("like_count"),
        "quote_count": metrics.get("quote_count"),
        "author_id": (author or {}).get("id"),
        "author_username": (author or {}).get("username"),
        "author_name": (author or {}).get("name"),
        "author_verified": (author or {}).get("verified"),
        "author_followers_count": author_metrics.get("followers_count"),
        "author_following_count": author_metrics.get("following_count"),
        "author_tweet_count": author_metrics.get("tweet_count"),
        "author_listed_count": author_metrics.get("listed_count"),
    }


def get_existing_tweet_ids(output_file: Path) -> set[str]:
    """Read existing tweet IDs from a CSV file."""
    if not output_file.exists() or output_file.stat().st_size == 0:
        return set()

    with output_file.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return {row["tweet_id"] for row in reader if "tweet_id" in row}


def get_most_recent_tweet_id(output_file: Path) -> Optional[str]:
    """Read a CSV file and return the ID of the most recent tweet."""
    if not output_file.exists() or output_file.stat().st_size == 0:
        return None

    most_recent_tweet = None
    try:
        with output_file.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            # Find the latest tweet in the file to avoid re-fetching old data.
            # ISO 8601 timestamps can be compared lexicographically.
            for row in reader:
                if row.get("tweet_created_at"):
                    if (
                        most_recent_tweet is None
                        or row["tweet_created_at"] > most_recent_tweet["tweet_created_at"]
                    ):
                        most_recent_tweet = row
    except (FileNotFoundError, StopIteration):
        return None

    return most_recent_tweet.get("tweet_id") if most_recent_tweet else None


def collect_query(
    client: TwitterClient,
    match: MatchConfig,
    query_config: QueryConfig,
    *,
    output_file: Path,
    sleep_seconds: float,
    append: bool,
    max_per_query: Optional[int] = None,
    since_id: Optional[str] = None,
    no_time_filter: bool = False,
) -> int:
    """Fetch tweets for a single query and persist them to disk."""

    effective_limit = (
        min(max_per_query, query_config.max_tweets)
        if max_per_query
        else query_config.max_tweets
    )
    if effective_limit <= 0:
        return 0

    output_file.parent.mkdir(parents=True, exist_ok=True)

    existing_tweet_ids = set()
    write_header = True

    if append and output_file.exists() and output_file.stat().st_size > 0:
        write_header = False
        mode = "a"
        # Read existing tweet IDs to perform client-side deduplication.
        existing_tweet_ids = get_existing_tweet_ids(output_file)
        print(f"  - Found {len(existing_tweet_ids)} existing tweets, will skip duplicates")
        
        # Auto-detect since_id from file if not provided and we want to use it
        if since_id is None and no_time_filter:
            since_id = get_most_recent_tweet_id(output_file)
            if since_id:
                print(f"  - Auto-detected since_id: {since_id}")
    else:
        if output_file.exists():
            output_file.unlink()
        mode = "w"

    # Auto-enable no_time_filter if since_id is provided (API restriction)
    if since_id:
        no_time_filter = True
        print(f"  - Using since_id={since_id}, time filters disabled (API requirement)")

    total_written = 0
    total_skipped = 0
    next_token: Optional[str] = None
    request_count = 0

    # Prepare API parameters
    api_params = query_config.additional_params.copy() if query_config.additional_params else {}
    if since_id:
        api_params["since_id"] = since_id

    with output_file.open(mode, encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        if write_header:
            writer.writeheader()

        while total_written < effective_limit:
            batch_size = min(100, effective_limit - total_written)
            
            # Use time filters only if not disabled
            start_time = None if no_time_filter else match.start_time
            end_time = None if no_time_filter else match.end_time
            
            payload = client.search_recent(
                query=query_config.query,
                start_time=start_time,
                end_time=end_time,
                next_token=next_token,
                max_results=batch_size,
                additional_params=api_params,
            )
            request_count += 1
            tweets = payload.get("data", [])
            includes = payload.get("includes", {})
            if not tweets:
                break

            user_map = {u["id"]: u for u in includes.get("users", [])}
            timestamp = datetime.now(timezone.utc).isoformat()

            for tweet in tweets:
                tweet_id = tweet.get("id")
                # Skip if we've already collected this tweet
                if tweet_id and tweet_id in existing_tweet_ids:
                    continue

                author = user_map.get(tweet.get("author_id"))
                row = build_row(
                    timestamp=timestamp,
                    match=match,
                    query_config=query_config,
                    tweet=tweet,
                    author=author,
                )
                writer.writerow(row)
                total_written += 1
                if tweet_id:
                    existing_tweet_ids.add(tweet_id)

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
            output_filename = f"{match.match_id}_{query_config.language}.csv"
            output_path = Path(args.output_dir) / output_filename
            written = collect_query(
                client,
                match,
                query_config,
                output_file=output_path,
                sleep_seconds=args.sleep,
                append=args.append,
                max_per_query=args.max_per_query,
                since_id=args.since_id,
                no_time_filter=args.no_time_filter,
            )
            total += written

    print(f"Done. Stored {total} tweets across {len(matches)} match(es).")


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except TwitterAPIError as exc:
        raise SystemExit(f"Request to X API failed: {exc}")
