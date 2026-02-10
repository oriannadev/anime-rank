# anime-rank

A beautiful CLI tool for exploring anime stats from your terminal, powered by the [Jikan API](https://jikan.moe/) (MyAnimeList).

No API key required. Just install and go.

## Features

- **Search** anime by name with rich, color-coded tables
- **Top anime** rankings filtered by type (TV, movie, OVA, etc.)
- **Detailed info** for any anime -- synopsis, genres, studios, stats
- **Seasonal** anime for the current season or any past/future season
- **Random** anime recommendations when you can't decide what to watch
- **Compare** two anime side by side

All output uses [Rich](https://github.com/Textualize/rich) for gorgeous terminal rendering with color-coded scores, formatted tables, and styled panels.

## Installation

```bash
# Clone the repo
git clone https://github.com/oriannadev/anime-rank.git
cd anime-rank

# Install (editable mode for development)
pip install -e ".[dev]"
```

### Requirements

- Python 3.9+
- An internet connection (Jikan API is free and public)

## Usage

### Search anime

```bash
anime-rank search naruto
anime-rank search "attack on titan" --limit 5
```

```
                    Search Results for 'naruto'
 ┌────────┬──────────────────────────────┬───────┬──────────┬─────────────────┬────────┐
 │     ID │ Title                        │ Score │ Episodes │ Status          │  Type  │
 ├────────┼──────────────────────────────┼───────┼──────────┼─────────────────┼────────┤
 │     20 │ Naruto                       │  8.00 │      220 │ Finished Airing │   TV   │
 │   1735 │ Naruto: Shippuuden           │  8.25 │      500 │ Finished Airing │   TV   │
 │  34566 │ Boruto: Naruto Next Gene...  │  5.73 │      293 │ Finished Airing │   TV   │
 └────────┴──────────────────────────────┴───────┴──────────┴─────────────────┴────────┘
  Use anime-rank info <ID> for details
```

### Top anime

```bash
anime-rank top
anime-rank top --type tv --limit 5
anime-rank top --type movie --limit 10
```

```
                    Top Anime (TV)
 ┌────┬────────┬──────────────────────────────┬───────┬──────────┬─────────────┐
 │  # │     ID │ Title                        │ Score │ Episodes │     Members │
 ├────┼────────┼──────────────────────────────┼───────┼──────────┼─────────────┤
 │  1 │   5114 │ Fullmetal Alchemist: Brot... │  9.10 │       64 │   3,200,000 │
 │  2 │  16498 │ Shingeki no Kyojin           │  8.54 │       25 │   3,700,000 │
 │  3 │  11061 │ Hunter x Hunter (2011)       │  9.04 │      148 │   2,400,000 │
 └────┴────────┴──────────────────────────────┴───────┴──────────┴─────────────┘
```

### Anime details

```bash
anime-rank info 1       # Cowboy Bebop
anime-rank info 5114    # FMA: Brotherhood
```

```
 Cowboy Bebop
 カウボーイビバップ

   Score       8.75
   Scored By   900,000
   Rank        #28
   Popularity  #39
   Type        TV
   Episodes    26
   Status      Finished Airing
   Aired       Apr 3, 1998 to Apr 24, 1999

   Genres      Action, Sci-Fi
   Studios     Sunrise

 ╭─ Synopsis ──────────────────────────────────╮
 │ In the year 2071, humanity has colonized    │
 │ several planets...                          │
 ╰─────────────────────────────────────────────╯

   MAL: https://myanimelist.net/anime/1/Cowboy_Bebop
```

### Seasonal anime

```bash
anime-rank seasonal                              # current season
anime-rank seasonal --year 2024 --season winter  # specific season
```

### Random recommendation

```bash
anime-rank random
```

```
 ╭──────────── Random Anime Recommendation ────────────╮
 │                                                      │
 │  Fullmetal Alchemist: Brotherhood                    │
 │                                                      │
 │    Score:    9.10                                     │
 │    Episodes: 64                                      │
 │    Status:   Finished Airing                         │
 │    Genres:   Action, Adventure, Fantasy              │
 │                                                      │
 │    After a horrific alchemy experiment goes wrong... │
 │                                                      │
 ╰──────────────────────────────── MAL ID: 5114 ───────╯
```

### Compare two anime

```bash
anime-rank compare 1 5114   # Cowboy Bebop vs FMA:B
```

```
                         Anime Comparison
 ┌────────────┬──────────────────────┬───────────────────────────────┐
 │ Attribute  │ Cowboy Bebop         │ Fullmetal Alchemist: Brothe...│
 ├────────────┼──────────────────────┼───────────────────────────────┤
 │ Score      │ 8.75                 │ 9.10                          │
 │ Rank       │ #28                  │ #1                            │
 │ Popularity │ #39                  │ #3                            │
 │ Episodes   │ 26                   │ 64                            │
 │ Genres     │ Action, Sci-Fi       │ Action, Adventure, Fantasy    │
 │ Studios    │ Sunrise              │ Bones                         │
 └────────────┴──────────────────────┴───────────────────────────────┘
```

## Score Color Coding

Scores are color-coded for quick readability:

- **Green** -- 8.0 and above (great)
- **Yellow** -- 6.0 to 7.99 (decent)
- **Red** -- below 6.0 (rough)

## API Rate Limits

The Jikan API allows 3 requests per second. anime-rank handles this automatically with built-in rate limiting and retry logic. You should never hit a rate limit during normal usage.

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest -v

# Run a specific test file
pytest tests/test_client.py -v
```

### Project Structure

```
anime-rank/
  anime_rank/
    __init__.py      # Version info
    cli.py           # Click CLI commands
    client.py        # Jikan API client (httpx, async)
    display.py       # Rich output formatting
  tests/
    conftest.py      # Shared fixtures and sample data
    test_cli.py      # CLI integration tests
    test_client.py   # API client tests (mocked with respx)
    test_display.py  # Display formatting unit tests
  pyproject.toml
  README.md
  LICENSE
  .gitignore
```

## Tech Stack

| Component   | Library                                            |
| ----------- | -------------------------------------------------- |
| CLI         | [Click](https://click.palletsprojects.com/)        |
| Display     | [Rich](https://github.com/Textualize/rich)         |
| HTTP Client | [httpx](https://www.python-httpx.org/)             |
| Testing     | [pytest](https://pytest.org/) + respx              |
| API         | [Jikan v4](https://docs.api.jikan.moe/) (free)    |

## License

MIT License. See [LICENSE](LICENSE) for details.
