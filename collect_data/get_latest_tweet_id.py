#!/usr/bin/env python3
"""Helper script to get the most recent tweet ID from a CSV file."""
import csv
import sys
from pathlib import Path


def get_latest_tweet_id(csv_path: Path) -> str | None:
    """Get the most recent tweet ID from a CSV file."""
    if not csv_path.exists():
        return None
    
    most_recent = None
    with csv_path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('tweet_created_at'):
                if most_recent is None or row['tweet_created_at'] > most_recent['tweet_created_at']:
                    most_recent = row
    
    return most_recent.get('tweet_id') if most_recent else None


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python get_latest_tweet_id.py <csv_file>")
        print("Example: python get_latest_tweet_id.py data/2025-10-21_arsenal_atletico_en.csv")
        sys.exit(1)
    
    csv_file = Path(sys.argv[1])
    tweet_id = get_latest_tweet_id(csv_file)
    
    if tweet_id:
        print(f"Latest tweet ID: {tweet_id}")
        print(f"\nUse with collector:")
        print(f"python -m collect_data.collector --since-id {tweet_id} --append ...")
    else:
        print("No tweets found in file or file doesn't exist")
        sys.exit(1)
