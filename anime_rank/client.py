"""Jikan API client with rate limiting and error handling."""

from __future__ import annotations

import asyncio
import time
from typing import Any, Optional

import httpx

BASE_URL = "https://api.jikan.moe/v4"

# Jikan enforces 3 requests/second. We track timestamps to stay under.
_request_timestamps: list[float] = []
_RATE_LIMIT = 3
_RATE_WINDOW = 1.0  # seconds


class JikanAPIError(Exception):
    """Raised when the Jikan API returns a non-success response."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(f"Jikan API error {status_code}: {message}")


class JikanClient:
    """Async HTTP client for the Jikan v4 API.

    Handles rate limiting (3 req/s), retries on 429, and timeout management.
    """

    def __init__(
        self,
        base_url: str = BASE_URL,
        timeout: float = 15.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={"Accept": "application/json"},
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    # -- rate limiter ----------------------------------------------------------

    @staticmethod
    async def _wait_for_rate_limit() -> None:
        """Sleep if necessary to respect the 3-requests-per-second limit."""
        now = time.monotonic()
        # Prune timestamps older than the window
        while _request_timestamps and now - _request_timestamps[0] > _RATE_WINDOW:
            _request_timestamps.pop(0)

        if len(_request_timestamps) >= _RATE_LIMIT:
            wait = _RATE_WINDOW - (now - _request_timestamps[0]) + 0.05
            if wait > 0:
                await asyncio.sleep(wait)

        _request_timestamps.append(time.monotonic())

    # -- core request ----------------------------------------------------------

    async def _request(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        retries: int = 2,
    ) -> dict[str, Any]:
        """Make a GET request with rate limiting, retry on 429."""
        await self._wait_for_rate_limit()
        client = await self._get_client()

        for attempt in range(retries + 1):
            try:
                resp = await client.get(endpoint, params=params)
            except httpx.TimeoutException:
                if attempt < retries:
                    await asyncio.sleep(1.0)
                    continue
                raise JikanAPIError(0, "Request timed out after multiple attempts")
            except httpx.ConnectError:
                raise JikanAPIError(0, "Could not connect to the Jikan API. Check your internet connection.")

            if resp.status_code == 200:
                return resp.json()

            if resp.status_code == 429:
                # Rate limited -- back off and retry
                retry_after = float(resp.headers.get("Retry-After", "1"))
                await asyncio.sleep(retry_after)
                continue

            if resp.status_code == 404:
                raise JikanAPIError(404, "Resource not found")

            raise JikanAPIError(resp.status_code, resp.text[:200])

        raise JikanAPIError(429, "Rate limited after retries")

    # -- public endpoints ------------------------------------------------------

    async def search_anime(
        self,
        query: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Search anime by name."""
        data = await self._request("/anime", params={"q": query, "limit": limit})
        return data.get("data", [])

    async def get_top_anime(
        self,
        anime_type: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Get top-rated anime, optionally filtered by type."""
        params: dict[str, Any] = {"limit": limit}
        if anime_type:
            params["type"] = anime_type
        data = await self._request("/top/anime", params=params)
        return data.get("data", [])

    async def get_anime_by_id(self, mal_id: int) -> dict[str, Any]:
        """Get full details for a single anime."""
        data = await self._request(f"/anime/{mal_id}/full")
        return data.get("data", {})

    async def get_seasonal_anime(
        self,
        year: Optional[int] = None,
        season: Optional[str] = None,
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        """Get anime for a given season, or the current season."""
        if year and season:
            endpoint = f"/seasons/{year}/{season}"
        else:
            endpoint = "/seasons/now"
        data = await self._request(endpoint, params={"limit": limit})
        return data.get("data", [])

    async def get_random_anime(self) -> dict[str, Any]:
        """Get a random anime."""
        data = await self._request("/random/anime")
        return data.get("data", {})

    async def get_anime_statistics(self, mal_id: int) -> dict[str, Any]:
        """Get watching/completed/dropped stats for an anime."""
        data = await self._request(f"/anime/{mal_id}/statistics")
        return data.get("data", {})
