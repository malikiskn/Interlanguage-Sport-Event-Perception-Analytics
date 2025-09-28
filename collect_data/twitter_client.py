"""HTTP client utilities for interacting with the X (Twitter) REST API v2."""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests


class TwitterAPIError(RuntimeError):
    """Raised when the X API returns an error response."""


class TwitterRateLimitError(TwitterAPIError):
    """Raised when the X API rate limit is reached."""


@dataclass
class TwitterClient:
    """Simple wrapper around the X API v2 search endpoint."""

    bearer_token: str
    request_timeout: int = 15
    max_retries: int = 5
    backoff_seconds: float = 2.0

    BASE_URL: str = "https://api.twitter.com/2/tweets/search/recent"

    def __post_init__(self) -> None:
        if not self.bearer_token:
            raise ValueError("A valid X API bearer token is required.")
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self.bearer_token}",
            "User-Agent": "LC-Sentiment-Collector/1.0",
        })

    def search_recent(
        self,
        *,
        query: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        next_token: Optional[str] = None,
        max_results: int = 100,
        additional_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Call the recent search endpoint and return the JSON payload."""
        params: Dict[str, Any] = {
            "query": query,
            "max_results": max(10, min(max_results, 100)),
            "tweet.fields": "id,text,lang,created_at,public_metrics,referenced_tweets,conversation_id,"\
                             "context_annotations,entities,author_id,possibly_sensitive,source",
            "expansions": "author_id,referenced_tweets.id,referenced_tweets.id.author_id",
            "user.fields": "id,name,username,public_metrics,description,location,verified,created_at",
        }
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        if next_token:
            params["next_token"] = next_token
        if additional_params:
            params.update(additional_params)

        last_error: Optional[Exception] = None
        for attempt in range(self.max_retries):
            response = self._session.get(self.BASE_URL, params=params, timeout=self.request_timeout)

            if response.status_code == 200:
                return response.json()

            if response.status_code == 429:
                retry_after = float(response.headers.get("x-rate-limit-reset", 0)) - time.time()
                sleep_for = max(self.backoff_seconds * (attempt + 1), retry_after)
                if sleep_for <= 0:
                    sleep_for = self.backoff_seconds * (attempt + 1)
                time.sleep(min(sleep_for, 60))
                last_error = TwitterRateLimitError("Rate limit reached. Retrying...")
                continue

            if 500 <= response.status_code < 600:
                time.sleep(self.backoff_seconds * (attempt + 1))
                last_error = TwitterAPIError(
                    f"Server error {response.status_code}: {response.text}"
                )
                continue

            raise TwitterAPIError(
                f"Error {response.status_code} while calling X API: {response.text}"
            )

        if last_error:
            raise last_error
        raise TwitterAPIError("Failed to reach X API after several retries.")
