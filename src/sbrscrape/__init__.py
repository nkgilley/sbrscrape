from datetime import datetime
import requests
import re
import json

sport_dict = {"NBA": "nba-basketball",
              "NFL": "nfl-football",
              "NHL": "nhl-hockey",
              "MLB": "mlb-baseball",
              "NCAAB": "ncaa-basketball"}

def scrape_games(sport="NBA", date="", current_line=True):
    if date == "":
        date = datetime.today().strftime("%Y-%m-%d")
    _line = 'currentLine' if current_line else 'openingLine'

    spreads = moneylines = totals = []
  
    spread_url = f"https://www.sportsbookreview.com/betting-odds/{sport_dict[sport]}/?date={date}"
    r = requests.get(spread_url)
    j = re.findall('__NEXT_DATA__" type="application/json">(.*?)</script>',r.text)
    try:
        spreads = json.loads(j[0])['props']['pageProps']['oddsTables'][0]['oddsTableModel']['gameRows']
    except IndexError:
        return []

    moneyline_url = f"https://www.sportsbookreview.com/betting-odds/{sport_dict[sport]}/money-line/full-game/?date={date}"
    r = requests.get(moneyline_url)
    j = re.findall('__NEXT_DATA__" type="application/json">(.*?)</script>',r.text)
    try:
        moneylines = json.loads(j[0])['props']['pageProps']['oddsTables'][0]['oddsTableModel']['gameRows']
    except IndexError:
        return []

    totals_url = f"https://www.sportsbookreview.com/betting-odds/{sport_dict[sport]}/totals/full-game/?date={date}"
    r = requests.get(totals_url)
    j = re.findall('__NEXT_DATA__" type="application/json">(.*?)</script>',r.text)
    try:
        totals = json.loads(j[0])['props']['pageProps']['oddsTables'][0]['oddsTableModel']['gameRows']
    except IndexError:
        return []

    all_stats = []
    for idx, game in enumerate(spreads):
        all_stats.append(game)
        all_stats[idx]['moneylines'] = moneylines[idx]
        all_stats[idx]['totals'] = totals[idx]

    games = []
    for event in all_stats:
        game = {}
        game['date'] = event['gameView']['startDate']
        game['status'] = event['gameView']['gameStatusText']
        game['home_team'] = event['gameView']['homeTeam']['fullName']
        game['home_team_loc'] = event['gameView']['homeTeam']['displayName']
        game['home_team_abbr'] = event['gameView']['homeTeam']['shortName']
        game['home_team_rank'] = event['gameView']['homeTeam']['rank']
        game['away_team'] = event['gameView']['awayTeam']['fullName']
        game['away_team_loc'] = event['gameView']['awayTeam']['displayName']
        game['away_team_abbr'] = event['gameView']['awayTeam']['shortName']
        game['away_team_rank'] = event['gameView']['awayTeam']['rank']
        game['home_score'] = event['gameView']['homeTeamScore']
        game['away_score'] = event['gameView']['awayTeamScore']
        game['home_spread'] = {}
        game['home_spread_odds'] = {}
        game['away_spread'] = {}
        game['away_spread_odds'] = {}
        game['under_odds'] = {}
        game['over_odds'] = {}
        game['total'] = {}
        game['home_ml'] = {}
        game['away_ml'] = {}
        if 'oddsViews' in event:
            for line in event['oddsViews']:
                if not line:
                    continue
                game['home_spread'][line['sportsbook']] = line[_line]['homeSpread']
                game['home_spread_odds'][line['sportsbook']] = line[_line]['homeOdds']
                game['away_spread'][line['sportsbook']] = line[_line]['awaySpread']
                game['away_spread_odds'][line['sportsbook']] = line[_line]['awayOdds']
        if 'totals' in event and 'oddsViews' in event['totals']:
            for line in event['totals']['oddsViews']:
                if not line:
                    continue
                game['under_odds'][line['sportsbook']] = line[_line]['underOdds']
                game['over_odds'][line['sportsbook']] = line[_line]['overOdds']
                game['total'][line['sportsbook']] = line[_line]['total']
        if 'moneylines' in event and 'oddsViews' in event['moneylines'] and event['moneylines']['oddsViews']:
            for line in event['moneylines']['oddsViews']:
                if not line:
                    continue
                game['home_ml'][line['sportsbook']] = line[_line]['homeOdds']
                game['away_ml'][line['sportsbook']] = line[_line]['awayOdds']
        games.append(game)
    return games


class Scoreboard:
    def __init__(self, sport='NBA', date="", sportsbook="draftkings"):
        try:
            self.games = scrape_games(sport, date, sportsbook)
        except Exception as e:
            print("An error occurred: {}".format(e))
            self.games = []
