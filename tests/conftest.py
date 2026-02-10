"""Shared test fixtures and sample data for anime-rank tests."""

from __future__ import annotations

import pytest


# -- sample API response payloads -----------------------------------------------

SAMPLE_ANIME_BRIEF = {
    "mal_id": 1,
    "title": "Cowboy Bebop",
    "title_english": "Cowboy Bebop",
    "title_japanese": "カウボーイビバップ",
    "type": "TV",
    "episodes": 26,
    "status": "Finished Airing",
    "score": 8.75,
    "scored_by": 900000,
    "rank": 28,
    "popularity": 39,
    "members": 1800000,
    "favorites": 75000,
    "source": "Original",
    "rating": "R - 17+ (violence & profanity)",
    "duration": "24 min per ep",
    "genres": [
        {"mal_id": 1, "name": "Action"},
        {"mal_id": 24, "name": "Sci-Fi"},
    ],
    "themes": [
        {"mal_id": 29, "name": "Space"},
    ],
    "studios": [
        {"mal_id": 14, "name": "Sunrise"},
    ],
    "producers": [
        {"mal_id": 23, "name": "Bandai Visual"},
    ],
    "aired": {
        "string": "Apr 3, 1998 to Apr 24, 1999",
    },
    "synopsis": "In the year 2071, humanity has colonized several planets.",
    "url": "https://myanimelist.net/anime/1/Cowboy_Bebop",
}

SAMPLE_ANIME_2 = {
    "mal_id": 5114,
    "title": "Fullmetal Alchemist: Brotherhood",
    "title_english": "Fullmetal Alchemist: Brotherhood",
    "title_japanese": "鋼の錬金術師",
    "type": "TV",
    "episodes": 64,
    "status": "Finished Airing",
    "score": 9.10,
    "scored_by": 2000000,
    "rank": 1,
    "popularity": 3,
    "members": 3200000,
    "favorites": 220000,
    "source": "Manga",
    "rating": "R - 17+ (violence & profanity)",
    "duration": "24 min per ep",
    "genres": [
        {"mal_id": 1, "name": "Action"},
        {"mal_id": 2, "name": "Adventure"},
        {"mal_id": 10, "name": "Fantasy"},
    ],
    "themes": [
        {"mal_id": 38, "name": "Military"},
    ],
    "studios": [
        {"mal_id": 4, "name": "Bones"},
    ],
    "producers": [
        {"mal_id": 17, "name": "Aniplex"},
    ],
    "aired": {
        "string": "Apr 5, 2009 to Jul 4, 2010",
    },
    "synopsis": "After a horrific alchemy experiment goes wrong.",
    "url": "https://myanimelist.net/anime/5114/FMA_Brotherhood",
}

SAMPLE_SEARCH_RESPONSE = {
    "data": [SAMPLE_ANIME_BRIEF],
    "pagination": {"last_visible_page": 1, "has_next_page": False},
}

SAMPLE_TOP_RESPONSE = {
    "data": [SAMPLE_ANIME_2, SAMPLE_ANIME_BRIEF],
    "pagination": {"last_visible_page": 1, "has_next_page": False},
}

SAMPLE_SEASONAL_RESPONSE = {
    "data": [SAMPLE_ANIME_BRIEF, SAMPLE_ANIME_2],
    "pagination": {"last_visible_page": 1, "has_next_page": False},
}

SAMPLE_FULL_RESPONSE = {
    "data": SAMPLE_ANIME_BRIEF,
}

SAMPLE_RANDOM_RESPONSE = {
    "data": SAMPLE_ANIME_2,
}

SAMPLE_STATS_RESPONSE = {
    "data": {
        "watching": 150000,
        "completed": 800000,
        "on_hold": 50000,
        "dropped": 30000,
        "plan_to_watch": 200000,
        "total": 1230000,
    },
}
