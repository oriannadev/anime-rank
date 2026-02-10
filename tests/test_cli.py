"""Tests for the Click CLI commands (all API calls mocked)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from click.testing import CliRunner

from anime_rank.cli import cli
from tests.conftest import (
    SAMPLE_ANIME_BRIEF,
    SAMPLE_ANIME_2,
)


@pytest.fixture
def runner():
    return CliRunner()


# -- version -------------------------------------------------------------------

def test_version(runner):
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "anime-rank" in result.output
    assert "1.0.0" in result.output


# -- search --------------------------------------------------------------------

@patch("anime_rank.cli.JikanClient")
def test_search_command(mock_client_cls, runner):
    instance = mock_client_cls.return_value
    instance.search_anime = AsyncMock(return_value=[SAMPLE_ANIME_BRIEF])
    instance.close = AsyncMock()

    result = runner.invoke(cli, ["search", "Cowboy", "Bebop"])
    assert result.exit_code == 0
    assert "Cowboy Bebop" in result.output
    instance.search_anime.assert_awaited_once_with("Cowboy Bebop", limit=10)


@patch("anime_rank.cli.JikanClient")
def test_search_with_limit(mock_client_cls, runner):
    instance = mock_client_cls.return_value
    instance.search_anime = AsyncMock(return_value=[SAMPLE_ANIME_BRIEF])
    instance.close = AsyncMock()

    result = runner.invoke(cli, ["search", "Bebop", "--limit", "5"])
    assert result.exit_code == 0
    instance.search_anime.assert_awaited_once_with("Bebop", limit=5)


# -- top -----------------------------------------------------------------------

@patch("anime_rank.cli.JikanClient")
def test_top_command(mock_client_cls, runner):
    instance = mock_client_cls.return_value
    instance.get_top_anime = AsyncMock(return_value=[SAMPLE_ANIME_2, SAMPLE_ANIME_BRIEF])
    instance.close = AsyncMock()

    result = runner.invoke(cli, ["top"])
    assert result.exit_code == 0
    assert "Fullmetal Alchemist" in result.output


@patch("anime_rank.cli.JikanClient")
def test_top_with_type(mock_client_cls, runner):
    instance = mock_client_cls.return_value
    instance.get_top_anime = AsyncMock(return_value=[SAMPLE_ANIME_BRIEF])
    instance.close = AsyncMock()

    result = runner.invoke(cli, ["top", "--type", "tv", "--limit", "5"])
    assert result.exit_code == 0
    instance.get_top_anime.assert_awaited_once_with(anime_type="tv", limit=5)


# -- info ----------------------------------------------------------------------

@patch("anime_rank.cli.JikanClient")
def test_info_command(mock_client_cls, runner):
    instance = mock_client_cls.return_value
    instance.get_anime_by_id = AsyncMock(return_value=SAMPLE_ANIME_BRIEF)
    instance.close = AsyncMock()

    result = runner.invoke(cli, ["info", "1"])
    assert result.exit_code == 0
    assert "Cowboy Bebop" in result.output
    instance.get_anime_by_id.assert_awaited_once_with(1)


@patch("anime_rank.cli.JikanClient")
def test_info_not_found(mock_client_cls, runner):
    from anime_rank.client import JikanAPIError

    instance = mock_client_cls.return_value
    instance.get_anime_by_id = AsyncMock(side_effect=JikanAPIError(404, "Not found"))
    instance.close = AsyncMock()

    result = runner.invoke(cli, ["info", "9999999"])
    assert result.exit_code != 0
    assert "not found" in result.output.lower()


# -- seasonal ------------------------------------------------------------------

@patch("anime_rank.cli.JikanClient")
def test_seasonal_current(mock_client_cls, runner):
    instance = mock_client_cls.return_value
    instance.get_seasonal_anime = AsyncMock(return_value=[SAMPLE_ANIME_BRIEF])
    instance.close = AsyncMock()

    result = runner.invoke(cli, ["seasonal"])
    assert result.exit_code == 0
    instance.get_seasonal_anime.assert_awaited_once_with(year=None, season=None, limit=25)


@patch("anime_rank.cli.JikanClient")
def test_seasonal_specific(mock_client_cls, runner):
    instance = mock_client_cls.return_value
    instance.get_seasonal_anime = AsyncMock(return_value=[SAMPLE_ANIME_BRIEF])
    instance.close = AsyncMock()

    result = runner.invoke(cli, ["seasonal", "--year", "2024", "--season", "winter"])
    assert result.exit_code == 0
    instance.get_seasonal_anime.assert_awaited_once_with(year=2024, season="winter", limit=25)


def test_seasonal_partial_args(runner):
    """Providing only --year without --season should error."""
    result = runner.invoke(cli, ["seasonal", "--year", "2024"])
    assert result.exit_code != 0
    assert "both" in result.output.lower() or "Provide both" in result.output


# -- random --------------------------------------------------------------------

@patch("anime_rank.cli.JikanClient")
def test_random_command(mock_client_cls, runner):
    instance = mock_client_cls.return_value
    instance.get_random_anime = AsyncMock(return_value=SAMPLE_ANIME_2)
    instance.close = AsyncMock()

    result = runner.invoke(cli, ["random"])
    assert result.exit_code == 0
    assert "Fullmetal Alchemist" in result.output


# -- compare -------------------------------------------------------------------

@patch("anime_rank.cli.JikanClient")
def test_compare_command(mock_client_cls, runner):
    instance = mock_client_cls.return_value
    instance.get_anime_by_id = AsyncMock(
        side_effect=[SAMPLE_ANIME_BRIEF, SAMPLE_ANIME_2]
    )
    instance.close = AsyncMock()

    result = runner.invoke(cli, ["compare", "1", "5114"])
    assert result.exit_code == 0
    assert "Cowboy Bebop" in result.output
    assert "Fullmetal Alchemist" in result.output
