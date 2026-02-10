"""Tests for the Jikan API client (all responses mocked)."""

from __future__ import annotations

import pytest
import httpx
import respx

from anime_rank.client import JikanClient, JikanAPIError, BASE_URL, _request_timestamps
from tests.conftest import (
    SAMPLE_SEARCH_RESPONSE,
    SAMPLE_TOP_RESPONSE,
    SAMPLE_FULL_RESPONSE,
    SAMPLE_RANDOM_RESPONSE,
    SAMPLE_SEASONAL_RESPONSE,
)


@pytest.fixture(autouse=True)
def _clear_rate_timestamps():
    """Reset the rate limiter between tests."""
    _request_timestamps.clear()
    yield
    _request_timestamps.clear()


@pytest.fixture
def client():
    return JikanClient(base_url=BASE_URL, timeout=5.0)


# -- search_anime --------------------------------------------------------------

@respx.mock
@pytest.mark.asyncio
async def test_search_anime_returns_results(client):
    respx.get(f"{BASE_URL}/anime").mock(
        return_value=httpx.Response(200, json=SAMPLE_SEARCH_RESPONSE)
    )
    results = await client.search_anime("Cowboy Bebop")
    await client.close()

    assert len(results) == 1
    assert results[0]["mal_id"] == 1
    assert results[0]["title"] == "Cowboy Bebop"


@respx.mock
@pytest.mark.asyncio
async def test_search_anime_empty(client):
    respx.get(f"{BASE_URL}/anime").mock(
        return_value=httpx.Response(200, json={"data": []})
    )
    results = await client.search_anime("nonexistenttitle12345")
    await client.close()

    assert results == []


# -- get_top_anime -------------------------------------------------------------

@respx.mock
@pytest.mark.asyncio
async def test_get_top_anime(client):
    respx.get(f"{BASE_URL}/top/anime").mock(
        return_value=httpx.Response(200, json=SAMPLE_TOP_RESPONSE)
    )
    results = await client.get_top_anime(limit=10)
    await client.close()

    assert len(results) == 2
    assert results[0]["score"] == 9.10


@respx.mock
@pytest.mark.asyncio
async def test_get_top_anime_with_type(client):
    respx.get(f"{BASE_URL}/top/anime").mock(
        return_value=httpx.Response(200, json=SAMPLE_TOP_RESPONSE)
    )
    results = await client.get_top_anime(anime_type="tv", limit=5)
    await client.close()

    assert len(results) == 2


# -- get_anime_by_id -----------------------------------------------------------

@respx.mock
@pytest.mark.asyncio
async def test_get_anime_by_id(client):
    respx.get(f"{BASE_URL}/anime/1/full").mock(
        return_value=httpx.Response(200, json=SAMPLE_FULL_RESPONSE)
    )
    anime = await client.get_anime_by_id(1)
    await client.close()

    assert anime["mal_id"] == 1
    assert anime["title"] == "Cowboy Bebop"
    assert anime["score"] == 8.75


@respx.mock
@pytest.mark.asyncio
async def test_get_anime_by_id_not_found(client):
    respx.get(f"{BASE_URL}/anime/9999999/full").mock(
        return_value=httpx.Response(404, json={"status": 404, "message": "Not found"})
    )
    with pytest.raises(JikanAPIError) as exc_info:
        await client.get_anime_by_id(9999999)
    await client.close()

    assert exc_info.value.status_code == 404


# -- get_seasonal_anime --------------------------------------------------------

@respx.mock
@pytest.mark.asyncio
async def test_get_seasonal_anime_current(client):
    respx.get(f"{BASE_URL}/seasons/now").mock(
        return_value=httpx.Response(200, json=SAMPLE_SEASONAL_RESPONSE)
    )
    results = await client.get_seasonal_anime()
    await client.close()

    assert len(results) == 2


@respx.mock
@pytest.mark.asyncio
async def test_get_seasonal_anime_specific(client):
    respx.get(f"{BASE_URL}/seasons/2024/winter").mock(
        return_value=httpx.Response(200, json=SAMPLE_SEASONAL_RESPONSE)
    )
    results = await client.get_seasonal_anime(year=2024, season="winter")
    await client.close()

    assert len(results) == 2


# -- get_random_anime ----------------------------------------------------------

@respx.mock
@pytest.mark.asyncio
async def test_get_random_anime(client):
    respx.get(f"{BASE_URL}/random/anime").mock(
        return_value=httpx.Response(200, json=SAMPLE_RANDOM_RESPONSE)
    )
    anime = await client.get_random_anime()
    await client.close()

    assert anime["mal_id"] == 5114
    assert anime["title"] == "Fullmetal Alchemist: Brotherhood"


# -- error handling ------------------------------------------------------------

@respx.mock
@pytest.mark.asyncio
async def test_rate_limit_retries(client):
    route = respx.get(f"{BASE_URL}/anime").mock(
        side_effect=[
            httpx.Response(429, headers={"Retry-After": "0.1"}),
            httpx.Response(200, json=SAMPLE_SEARCH_RESPONSE),
        ]
    )
    results = await client.search_anime("test")
    await client.close()

    assert len(results) == 1
    assert route.call_count == 2


@respx.mock
@pytest.mark.asyncio
async def test_server_error_raises(client):
    respx.get(f"{BASE_URL}/anime").mock(
        return_value=httpx.Response(500, text="Internal Server Error")
    )
    with pytest.raises(JikanAPIError) as exc_info:
        await client.search_anime("test")
    await client.close()

    assert exc_info.value.status_code == 500
