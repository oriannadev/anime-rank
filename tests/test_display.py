"""Tests for Rich display formatting functions."""

from __future__ import annotations

from io import StringIO

from rich.console import Console

from anime_rank.display import (
    display_search_results,
    display_top_anime,
    display_anime_detail,
    display_seasonal_anime,
    display_random_anime,
    display_comparison,
    display_error,
    _score_text,
    _score_style,
    _truncate,
    _extract_names,
    _format_number,
)
from tests.conftest import SAMPLE_ANIME_BRIEF, SAMPLE_ANIME_2


# -- helper unit tests ---------------------------------------------------------

class TestScoreText:
    def test_high_score(self):
        assert _score_text(9.5) == "9.50"

    def test_zero_score(self):
        assert _score_text(0) == "0.00"

    def test_none_score(self):
        assert _score_text(None) == "N/A"


class TestScoreStyle:
    def test_high(self):
        assert "green" in _score_style(8.5)

    def test_mid(self):
        assert "yellow" in _score_style(7.0)

    def test_low(self):
        assert "red" in _score_style(4.0)

    def test_none(self):
        assert _score_style(None) == "dim"


class TestTruncate:
    def test_short_string(self):
        assert _truncate("hello", 10) == "hello"

    def test_long_string(self):
        result = _truncate("a" * 100, 20)
        assert len(result) == 20
        assert result.endswith("\u2026")

    def test_none_input(self):
        assert _truncate(None) == "N/A"

    def test_empty_string(self):
        assert _truncate("") == "N/A"


class TestExtractNames:
    def test_with_items(self):
        items = [{"name": "Action"}, {"name": "Sci-Fi"}]
        assert _extract_names(items) == "Action, Sci-Fi"

    def test_empty_list(self):
        assert _extract_names([]) == "N/A"

    def test_none(self):
        assert _extract_names(None) == "N/A"


class TestFormatNumber:
    def test_large_number(self):
        assert _format_number(1500000) == "1,500,000"

    def test_small_number(self):
        assert _format_number(42) == "42"

    def test_none(self):
        assert _format_number(None) == "N/A"


# -- display function tests (capture output) -----------------------------------

def _capture(func, *args, **kwargs) -> str:
    """Temporarily redirect the module-level console to a StringIO buffer."""
    import anime_rank.display as disp

    buf = StringIO()
    original = disp.console
    disp.console = Console(file=buf, force_terminal=True, width=120)
    try:
        func(*args, **kwargs)
    finally:
        disp.console = original
    return buf.getvalue()


class TestDisplaySearchResults:
    def test_with_results(self):
        output = _capture(display_search_results, [SAMPLE_ANIME_BRIEF], "Cowboy")
        assert "Cowboy Bebop" in output
        assert "8.75" in output
        assert "26" in output

    def test_no_results(self):
        output = _capture(display_search_results, [], "nope")
        assert "No results" in output


class TestDisplayTopAnime:
    def test_with_results(self):
        output = _capture(display_top_anime, [SAMPLE_ANIME_2, SAMPLE_ANIME_BRIEF], "tv")
        assert "Fullmetal Alchemist" in output
        assert "Cowboy Bebop" in output
        assert "TV" in output

    def test_no_type(self):
        output = _capture(display_top_anime, [SAMPLE_ANIME_BRIEF], None)
        assert "All" in output

    def test_empty(self):
        output = _capture(display_top_anime, [], "movie")
        assert "No top anime" in output


class TestDisplayAnimeDetail:
    def test_renders_full_detail(self):
        output = _capture(display_anime_detail, SAMPLE_ANIME_BRIEF)
        assert "Cowboy Bebop" in output
        assert "8.75" in output
        assert "Sunrise" in output
        assert "Action" in output
        assert "humanity has colonized" in output

    def test_empty(self):
        output = _capture(display_anime_detail, {})
        assert "not found" in output


class TestDisplaySeasonalAnime:
    def test_with_season(self):
        output = _capture(
            display_seasonal_anime,
            [SAMPLE_ANIME_BRIEF],
            2024,
            "winter",
        )
        assert "Winter 2024" in output
        assert "Cowboy Bebop" in output

    def test_current_season(self):
        output = _capture(display_seasonal_anime, [SAMPLE_ANIME_BRIEF], None, None)
        assert "Current Season" in output

    def test_empty(self):
        output = _capture(display_seasonal_anime, [], 2024, "spring")
        assert "No seasonal anime" in output


class TestDisplayRandomAnime:
    def test_renders(self):
        output = _capture(display_random_anime, SAMPLE_ANIME_2)
        assert "Fullmetal Alchemist" in output
        assert "Random" in output

    def test_empty(self):
        output = _capture(display_random_anime, {})
        assert "Could not fetch" in output


class TestDisplayComparison:
    def test_renders_both(self):
        output = _capture(display_comparison, SAMPLE_ANIME_BRIEF, SAMPLE_ANIME_2)
        assert "Cowboy Bebop" in output
        assert "Fullmetal Alchemist" in output
        assert "8.75" in output
        assert "9.10" in output

    def test_empty_anime(self):
        output = _capture(display_comparison, {}, SAMPLE_ANIME_2)
        assert "Could not load" in output


class TestDisplayError:
    def test_shows_message(self):
        output = _capture(display_error, "Something broke")
        assert "Something broke" in output
        assert "Error" in output
