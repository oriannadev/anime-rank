"""Rich-powered display formatting for anime-rank."""

from __future__ import annotations

from typing import Any, Optional

from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

# -- colour palette (dark-terminal friendly) -----------------------------------
CYAN = "cyan"
GREEN = "green"
YELLOW = "yellow"
MAGENTA = "magenta"
BOLD_CYAN = "bold cyan"
BOLD_GREEN = "bold green"
BOLD_YELLOW = "bold yellow"
BOLD_MAGENTA = "bold magenta"
DIM = "dim"
SCORE_HIGH = "bold green"
SCORE_MID = "bold yellow"
SCORE_LOW = "bold red"


# -- helpers -------------------------------------------------------------------

def _score_style(score: Optional[float]) -> str:
    """Return a Rich style string based on score value."""
    if score is None:
        return DIM
    if score >= 8.0:
        return SCORE_HIGH
    if score >= 6.0:
        return SCORE_MID
    return SCORE_LOW


def _score_text(score: Optional[float]) -> str:
    """Format a score for display."""
    if score is None:
        return "N/A"
    return f"{score:.2f}"


def _truncate(text: Optional[str], length: int = 80) -> str:
    """Truncate text to a given length, adding ellipsis if needed."""
    if not text:
        return "N/A"
    if len(text) <= length:
        return text
    return text[: length - 1] + "\u2026"


def _extract_names(items: Optional[list[dict[str, Any]]]) -> str:
    """Pull 'name' from a list of MAL entity dicts."""
    if not items:
        return "N/A"
    return ", ".join(item.get("name", "?") for item in items)


def _format_number(n: Optional[int]) -> str:
    """Format large numbers with commas."""
    if n is None:
        return "N/A"
    return f"{n:,}"


# -- public display functions --------------------------------------------------

def display_search_results(results: list[dict[str, Any]], query: str) -> None:
    """Render search results as a Rich table."""
    if not results:
        console.print(
            Panel(
                f"[{YELLOW}]No results found for '{query}'[/]",
                title="Search",
                border_style=CYAN,
            )
        )
        return

    table = Table(
        title=f"Search Results for '{query}'",
        title_style=BOLD_CYAN,
        border_style=CYAN,
        show_lines=True,
        padding=(0, 1),
    )
    table.add_column("ID", style=DIM, justify="right", width=7)
    table.add_column("Title", style=BOLD_GREEN, min_width=25, max_width=45)
    table.add_column("Score", justify="center", width=7)
    table.add_column("Episodes", justify="center", width=10)
    table.add_column("Status", width=16)
    table.add_column("Type", style=MAGENTA, justify="center", width=8)

    for anime in results:
        score = anime.get("score")
        table.add_row(
            str(anime.get("mal_id", "?")),
            _truncate(anime.get("title"), 44),
            Text(_score_text(score), style=_score_style(score)),
            str(anime.get("episodes") or "?"),
            anime.get("status", "?"),
            anime.get("type", "?"),
        )

    console.print()
    console.print(table)
    console.print(
        f"  [{DIM}]Use [bold]anime-rank info <ID>[/bold] for details[/]"
    )
    console.print()


def display_top_anime(results: list[dict[str, Any]], anime_type: Optional[str]) -> None:
    """Render top anime list as a Rich table."""
    label = anime_type.upper() if anime_type else "All"

    if not results:
        console.print(Panel(f"[{YELLOW}]No top anime found.[/]", border_style=CYAN))
        return

    table = Table(
        title=f"Top Anime ({label})",
        title_style=BOLD_MAGENTA,
        border_style=MAGENTA,
        show_lines=True,
        padding=(0, 1),
    )
    table.add_column("#", style=BOLD_YELLOW, justify="right", width=4)
    table.add_column("ID", style=DIM, justify="right", width=7)
    table.add_column("Title", style=BOLD_GREEN, min_width=25, max_width=45)
    table.add_column("Score", justify="center", width=7)
    table.add_column("Episodes", justify="center", width=10)
    table.add_column("Members", justify="right", width=12)

    for idx, anime in enumerate(results, start=1):
        score = anime.get("score")
        table.add_row(
            str(idx),
            str(anime.get("mal_id", "?")),
            _truncate(anime.get("title"), 44),
            Text(_score_text(score), style=_score_style(score)),
            str(anime.get("episodes") or "?"),
            _format_number(anime.get("members")),
        )

    console.print()
    console.print(table)
    console.print()


def display_anime_detail(anime: dict[str, Any]) -> None:
    """Render detailed anime info as a Rich panel with nested layout."""
    if not anime:
        console.print(Panel(f"[{YELLOW}]Anime not found.[/]", border_style=CYAN))
        return

    title = anime.get("title", "Unknown")
    title_en = anime.get("title_english")
    title_jp = anime.get("title_japanese")
    score = anime.get("score")
    scored_by = anime.get("scored_by")
    rank = anime.get("rank")
    popularity = anime.get("popularity")

    # -- header ----------------------------------------------------------------
    header_lines: list[str] = []
    if title_en and title_en != title:
        header_lines.append(f"[{BOLD_GREEN}]{title}[/]  [{DIM}]({title_en})[/]")
    else:
        header_lines.append(f"[{BOLD_GREEN}]{title}[/]")
    if title_jp:
        header_lines.append(f"[{DIM}]{title_jp}[/]")

    # -- stats block -----------------------------------------------------------
    stats_table = Table(show_header=False, box=None, padding=(0, 2))
    stats_table.add_column("label", style=BOLD_CYAN)
    stats_table.add_column("value")

    stats_table.add_row("Score", Text(_score_text(score), style=_score_style(score)))
    if scored_by:
        stats_table.add_row("Scored By", _format_number(scored_by))
    if rank:
        stats_table.add_row("Rank", f"#{rank}")
    if popularity:
        stats_table.add_row("Popularity", f"#{popularity}")
    stats_table.add_row("Type", anime.get("type", "?"))
    stats_table.add_row("Source", anime.get("source", "?"))
    stats_table.add_row("Episodes", str(anime.get("episodes") or "?"))
    stats_table.add_row("Status", anime.get("status", "?"))

    aired = anime.get("aired", {})
    aired_str = aired.get("string", "?") if aired else "?"
    stats_table.add_row("Aired", aired_str)

    stats_table.add_row("Duration", anime.get("duration", "?"))
    stats_table.add_row("Rating", anime.get("rating", "?"))

    # -- metadata block --------------------------------------------------------
    meta_table = Table(show_header=False, box=None, padding=(0, 2))
    meta_table.add_column("label", style=BOLD_MAGENTA)
    meta_table.add_column("value")

    meta_table.add_row("Genres", _extract_names(anime.get("genres")))
    meta_table.add_row("Themes", _extract_names(anime.get("themes")))
    meta_table.add_row("Studios", _extract_names(anime.get("studios")))
    meta_table.add_row("Producers", _extract_names(anime.get("producers")))
    meta_table.add_row(
        "Members", _format_number(anime.get("members")),
    )
    meta_table.add_row(
        "Favorites", _format_number(anime.get("favorites")),
    )

    # -- synopsis --------------------------------------------------------------
    synopsis = anime.get("synopsis") or "No synopsis available."

    # -- assemble panel --------------------------------------------------------
    header_text = "\n".join(header_lines)

    content_parts = [
        header_text,
        "",
        stats_table,
        "",
        meta_table,
        "",
        Panel(
            synopsis,
            title="Synopsis",
            title_align="left",
            border_style=GREEN,
            padding=(1, 2),
        ),
    ]

    group = Columns([], expand=True)  # unused but keeps import for future use

    console.print()
    for part in content_parts:
        if isinstance(part, str):
            console.print(part)
        else:
            console.print(part)

    # -- external links --------------------------------------------------------
    url = anime.get("url")
    if url:
        console.print(f"\n  [{DIM}]MAL: {url}[/]")
    console.print()


def display_seasonal_anime(
    results: list[dict[str, Any]],
    year: Optional[int],
    season: Optional[str],
) -> None:
    """Render seasonal anime as a Rich table."""
    label = f"{season.capitalize()} {year}" if season and year else "Current Season"

    if not results:
        console.print(
            Panel(f"[{YELLOW}]No seasonal anime found for {label}.[/]", border_style=CYAN)
        )
        return

    table = Table(
        title=f"Seasonal Anime - {label}",
        title_style=BOLD_YELLOW,
        border_style=YELLOW,
        show_lines=True,
        padding=(0, 1),
    )
    table.add_column("ID", style=DIM, justify="right", width=7)
    table.add_column("Title", style=BOLD_GREEN, min_width=25, max_width=40)
    table.add_column("Score", justify="center", width=7)
    table.add_column("Episodes", justify="center", width=10)
    table.add_column("Studios", style=CYAN, width=20)
    table.add_column("Genres", style=MAGENTA, width=22)

    for anime in results:
        score = anime.get("score")
        table.add_row(
            str(anime.get("mal_id", "?")),
            _truncate(anime.get("title"), 39),
            Text(_score_text(score), style=_score_style(score)),
            str(anime.get("episodes") or "?"),
            _truncate(_extract_names(anime.get("studios")), 19),
            _truncate(_extract_names(anime.get("genres")), 21),
        )

    console.print()
    console.print(table)
    console.print()


def display_random_anime(anime: dict[str, Any]) -> None:
    """Render a random anime recommendation as a flashy panel."""
    if not anime:
        console.print(Panel(f"[{YELLOW}]Could not fetch random anime.[/]", border_style=CYAN))
        return

    title = anime.get("title", "Unknown")
    title_en = anime.get("title_english")
    score = anime.get("score")
    episodes = anime.get("episodes") or "?"
    status = anime.get("status", "?")
    genres = _extract_names(anime.get("genres"))
    synopsis = _truncate(anime.get("synopsis") or "No synopsis.", 300)

    header = Text(title, style=BOLD_GREEN)
    if title_en and title_en != title:
        header.append("  ")
        header.append(f"({title_en})", style=DIM)

    score_label = Text("  Score:    ", style=BOLD_CYAN)
    score_label.append(_score_text(score), style=_score_style(score))

    body = Text()
    body.append_text(header)
    body.append("\n\n")
    body.append_text(score_label)
    body.append(f"\n  ")
    body.append("Episodes: ", style=BOLD_CYAN)
    body.append(str(episodes))
    body.append(f"\n  ")
    body.append("Status:   ", style=BOLD_CYAN)
    body.append(status)
    body.append(f"\n  ")
    body.append("Genres:   ", style=BOLD_CYAN)
    body.append(genres, style=MAGENTA)
    body.append(f"\n\n  {synopsis}")

    console.print()
    console.print(
        Panel(
            body,
            title="Random Anime Recommendation",
            title_align="center",
            subtitle=f"MAL ID: {anime.get('mal_id', '?')}",
            border_style=MAGENTA,
            padding=(1, 2),
        )
    )
    console.print()


def display_comparison(anime_a: dict[str, Any], anime_b: dict[str, Any]) -> None:
    """Render a side-by-side comparison of two anime."""
    if not anime_a or not anime_b:
        console.print(Panel(f"[{YELLOW}]Could not load one or both anime.[/]", border_style=CYAN))
        return

    table = Table(
        title="Anime Comparison",
        title_style=BOLD_CYAN,
        border_style=CYAN,
        show_lines=True,
        padding=(0, 1),
    )
    table.add_column("Attribute", style=BOLD_MAGENTA, width=14)
    table.add_column(
        _truncate(anime_a.get("title", "Anime A"), 35),
        style=GREEN,
        min_width=20,
        max_width=36,
    )
    table.add_column(
        _truncate(anime_b.get("title", "Anime B"), 35),
        style=GREEN,
        min_width=20,
        max_width=36,
    )

    fields: list[tuple[str, str, Any, Any]] = [
        ("Score", "score", anime_a.get("score"), anime_b.get("score")),
        ("Rank", "rank", anime_a.get("rank"), anime_b.get("rank")),
        ("Popularity", "popularity", anime_a.get("popularity"), anime_b.get("popularity")),
        ("Episodes", "episodes", anime_a.get("episodes"), anime_b.get("episodes")),
        ("Status", "status", anime_a.get("status"), anime_b.get("status")),
        ("Type", "type", anime_a.get("type"), anime_b.get("type")),
        ("Source", "source", anime_a.get("source"), anime_b.get("source")),
        ("Rating", "rating", anime_a.get("rating"), anime_b.get("rating")),
        ("Members", "members", anime_a.get("members"), anime_b.get("members")),
        ("Favorites", "favorites", anime_a.get("favorites"), anime_b.get("favorites")),
    ]

    for label, key, val_a, val_b in fields:
        if key == "score":
            cell_a = Text(_score_text(val_a), style=_score_style(val_a))
            cell_b = Text(_score_text(val_b), style=_score_style(val_b))
        elif key in ("rank", "popularity"):
            cell_a = f"#{val_a}" if val_a is not None else "N/A"
            cell_b = f"#{val_b}" if val_b is not None else "N/A"
        elif key in ("members", "favorites"):
            cell_a = _format_number(val_a)
            cell_b = _format_number(val_b)
        else:
            cell_a = str(val_a) if val_a is not None else "N/A"
            cell_b = str(val_b) if val_b is not None else "N/A"

        table.add_row(label, cell_a, cell_b)

    # Genres row
    table.add_row(
        "Genres",
        _extract_names(anime_a.get("genres")),
        _extract_names(anime_b.get("genres")),
    )
    # Studios row
    table.add_row(
        "Studios",
        _extract_names(anime_a.get("studios")),
        _extract_names(anime_b.get("studios")),
    )

    console.print()
    console.print(table)
    console.print()


def display_error(message: str) -> None:
    """Show a styled error panel."""
    console.print()
    console.print(
        Panel(
            f"[bold red]{message}[/]",
            title="Error",
            border_style="red",
            padding=(1, 2),
        )
    )
    console.print()
