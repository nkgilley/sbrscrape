# sbrscrape

Python script to scrape sports betting odds data from sbrodds.

```python
from sbrscrape import Scoreboard
games = Scoreboard(sport="NFL").games
games[0]
{
    "date": "2023-01-08T18:00:00+00:00",
    "status": "13:00 ET",
    "home_team": "Atlanta Falcons",
    "home_team_loc": "Atlanta",
    "home_team_abbr": "ATL",
    "home_team_rank": -1,
    "away_team": "Tampa Bay Buccaneers",
    "away_team_loc": "Tampa Bay",
    "away_team_abbr": "TB",
    "away_team_rank": -1,
    "home_score": 0,
    "away_score": 0,
    "home_spread": {
        "betmgm": -4,
        "draftkings": -4,
        "fanduel": -4.5,
        "caesars": -4,
        "pointsbet": -4,
        "wynn": -4,
        "bet_rivers_ny": -4
    },
    "home_spread_odds": {
        "betmgm": -110,
        "draftkings": -110,
        "fanduel": -104,
        "caesars": -110,
        "pointsbet": -110,
        "wynn": -110,
        "bet_rivers_ny": -113
    },
    "away_spread": {
        "betmgm": 4,
        "draftkings": 4,
        "fanduel": 4.5,
        "caesars": 4,
        "pointsbet": 4,
        "wynn": 4,
        "bet_rivers_ny": 4
    },
    "away_spread_odds": {
        "betmgm": -110,
        "draftkings": -110,
        "fanduel": -118,
        "caesars": -110,
        "pointsbet": -110,
        "wynn": -110,
        "bet_rivers_ny": -110
    },
    "under_odds": {
        "betmgm": -110,
        "draftkings": -110,
        "fanduel": -110,
        "caesars": -110,
        "pointsbet": -110,
        "wynn": -110,
        "bet_rivers_ny": -112
    },
    "over_odds": {
        "betmgm": -110,
        "draftkings": -110,
        "fanduel": -110,
        "caesars": -110,
        "pointsbet": -110,
        "wynn": -110,
        "bet_rivers_ny": -112
    },
    "total": {
        "betmgm": 40.5,
        "draftkings": 40.5,
        "fanduel": 40.5,
        "caesars": 40,
        "pointsbet": 40.5,
        "wynn": 40.5,
        "bet_rivers_ny": 40.5
    },
    "home_ml": {
        "betmgm": -200,
        "draftkings": -195,
        "fanduel": -194,
        "caesars": -196,
        "pointsbet": -210,
        "wynn": -204,
        "bet_rivers_ny": -200
    },
    "away_ml": {
        "betmgm": 165,
        "draftkings": 165,
        "fanduel": 164,
        "caesars": 162,
        "pointsbet": 175,
        "wynn": 170,
        "bet_rivers_ny": 175
    }
}
```