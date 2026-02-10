"""Click CLI entry point for anime-rank."""

from __future__ import annotations

import asyncio
import sys
from typing import Optional

import click
from rich.console import Console

from anime_rank import __version__
from anime_rank.client import JikanClient, JikanAPIError
from anime_rank.display import (
    display_anime_detail,
    display_comparison,
    display_error,
    display_random_anime,
    display_search_results,
    display_seasonal_anime,
    display_top_anime,
)

console = Console()


def _run(coro):
    """Run an async coroutine in a synchronous Click command."""
    return asyncio.run(coro)


def _handle_api_error(exc: JikanAPIError) -> None:
    """Translate API errors into friendly messages."""
    if exc.status_code == 404:
        display_error("That anime ID was not found on MyAnimeList.")
    elif exc.status_code == 429:
        display_error("Rate limited by the Jikan API. Wait a moment and try again.")
    elif exc.status_code == 0:
        display_error(exc.message)
    else:
        display_error(f"API returned status {exc.status_code}: {exc.message}")


# -- main group ----------------------------------------------------------------

@click.group()
@click.version_option(version=__version__, prog_name="anime-rank")
def cli() -> None:
    """Anime Rank -- explore anime stats from your terminal.

    Powered by the Jikan API (MyAnimeList).
    """


# -- search --------------------------------------------------------------------

@cli.command()
@click.argument("query", nargs=-1, required=True)
@click.option("--limit", "-l", default=10, show_default=True, help="Max results.")
def search(query: tuple[str, ...], limit: int) -> None:
    """Search anime by name."""
    query_str = " ".join(query)
    if not query_str.strip():
        display_error("Please provide a search query.")
        sys.exit(1)

    async def _search() -> None:
        client = JikanClient()
        try:
            results = await client.search_anime(query_str, limit=limit)
            display_search_results(results, query_str)
        except JikanAPIError as exc:
            _handle_api_error(exc)
            sys.exit(1)
        finally:
            await client.close()

    _run(_search())


# -- top -----------------------------------------------------------------------

@cli.command()
@click.option(
    "--type", "-t", "anime_type",
    type=click.Choice(["tv", "movie", "ova", "special", "ona", "music"], case_sensitive=False),
    default=None,
    help="Filter by anime type.",
)
@click.option("--limit", "-l", default=10, show_default=True, help="Number of results.")
def top(anime_type: Optional[str], limit: int) -> None:
    """Show top-rated anime."""

    async def _top() -> None:
        client = JikanClient()
        try:
            results = await client.get_top_anime(anime_type=anime_type, limit=limit)
            display_top_anime(results, anime_type)
        except JikanAPIError as exc:
            _handle_api_error(exc)
            sys.exit(1)
        finally:
            await client.close()

    _run(_top())


# -- info ----------------------------------------------------------------------

@cli.command()
@click.argument("mal_id", type=int)
def info(mal_id: int) -> None:
    """Show detailed info for an anime by its MyAnimeList ID."""

    async def _info() -> None:
        client = JikanClient()
        try:
            anime = await client.get_anime_by_id(mal_id)
            display_anime_detail(anime)
        except JikanAPIError as exc:
            _handle_api_error(exc)
            sys.exit(1)
        finally:
            await client.close()

    _run(_info())


# -- seasonal ------------------------------------------------------------------

@cli.command()
@click.option("--year", "-y", type=int, default=None, help="Year (e.g. 2026).")
@click.option(
    "--season", "-s",
    type=click.Choice(["winter", "spring", "summer", "fall"], case_sensitive=False),
    default=None,
    help="Season name.",
)
@click.option("--limit", "-l", default=25, show_default=True, help="Number of results.")
def seasonal(year: Optional[int], season: Optional[str], limit: int) -> None:
    """Show anime for the current or a specific season."""
    if (year is None) != (season is None):
        display_error("Provide both --year and --season, or neither for current season.")
        sys.exit(1)

    async def _seasonal() -> None:
        client = JikanClient()
        try:
            results = await client.get_seasonal_anime(year=year, season=season, limit=limit)
            display_seasonal_anime(results, year, season)
        except JikanAPIError as exc:
            _handle_api_error(exc)
            sys.exit(1)
        finally:
            await client.close()

    _run(_seasonal())


# -- random --------------------------------------------------------------------

@cli.command()
def random() -> None:
    """Get a random anime recommendation."""

    async def _random() -> None:
        client = JikanClient()
        try:
            anime = await client.get_random_anime()
            display_random_anime(anime)
        except JikanAPIError as exc:
            _handle_api_error(exc)
            sys.exit(1)
        finally:
            await client.close()

    _run(_random())


# -- compare -------------------------------------------------------------------

@cli.command()
@click.argument("id1", type=int)
@click.argument("id2", type=int)
def compare(id1: int, id2: int) -> None:
    """Compare two anime side by side (by MAL ID)."""

    async def _compare() -> None:
        client = JikanClient()
        try:
            anime_a, anime_b = await asyncio.gather(
                client.get_anime_by_id(id1),
                client.get_anime_by_id(id2),
            )
            display_comparison(anime_a, anime_b)
        except JikanAPIError as exc:
            _handle_api_error(exc)
            sys.exit(1)
        finally:
            await client.close()

    _run(_compare())


# -- entry point ---------------------------------------------------------------

def main() -> None:
    """Package entry point."""
    cli()


if __name__ == "__main__":
    main()
