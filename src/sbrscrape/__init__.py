from datetime import datetime
import requests
import re
import json

sport_dict = {"NBA": "nba-basketball",
              "NFL": "nfl-football",
              "NHL": "nhl-hockey",
              "MLB": "mlb-baseball",
              "NCAAB": "ncaa-basketball"}

class Scoreboard:
    def __init__(self, sport='NBA', date="", current_line=True):
        try:
            self.scrape_games(sport, date, current_line)
        except Exception as e:
            print("An error occurred: {}".format(e))
            self.games = []

    def scrape_games(self, sport="NBA", date="", current_line=True):
        if date == "":
            date = datetime.today().strftime("%Y-%m-%d")
        _line = 'currentLine' if current_line else 'openingLine'

        spreads = moneylines = totals = {}

        spread_url = f"https://www.sportsbookreview.com/betting-odds/{sport_dict[sport]}/?date={date}"
        r = requests.get(spread_url)
        j = re.findall('__NEXT_DATA__" type="application/json">(.*?)</script>',r.text)
        try:
            build_id = json.loads(j[0])['buildId']
            spreads_url = f"https://www.sportsbookreview.com/_next/data/{build_id}/betting-odds/{sport_dict[sport]}.json?league={sport_dict[sport]}&date={date}"
            spreads_json = requests.get(spreads_url).json()
            spreads_list = spreads_json['pageProps']['oddsTables'][0]['oddsTableModel']['gameRows']
            spreads = {g['gameView']['gameId']: g for g in spreads_list}
        except IndexError:
            return []

        moneyline_url = f"https://www.sportsbookreview.com/_next/data/{build_id}/betting-odds/{sport_dict[sport]}/money-line/full-game.json?league={sport_dict[sport]}&oddsType=money-line&oddsScope=full-game&date={date}"
        moneyline_json = requests.get(moneyline_url).json()
        moneylines_list = moneyline_json['pageProps']['oddsTables'][0]['oddsTableModel']['gameRows']
        moneylines = {g['gameView']['gameId']: g for g in moneylines_list}
        totals_url = f"https://www.sportsbookreview.com/_next/data/{build_id}/betting-odds/{sport_dict[sport]}/totals/full-game.json?league={sport_dict[sport]}&oddsType=totals&oddsScope=full-game&date={date}"
        totals_json = requests.get(totals_url).json()
        totals_list = totals_json['pageProps']['oddsTables'][0]['oddsTableModel']['gameRows']
        totals = {g['gameView']['gameId']: g for g in totals_list}

        all_stats = {
            game_id: {'spreads': spreads[game_id], 'moneylines': moneylines[game_id], 'totals': totals[game_id], } for game_id in spreads.keys()
        }

        games = []
        for event in all_stats.values():
            game = {}
            game['date'] = event['spreads']['gameView']['startDate']
            game['status'] = event['spreads']['gameView']['gameStatusText']
            game['home_team'] = event['spreads']['gameView']['homeTeam']['fullName']
            game['home_team_loc'] = event['spreads']['gameView']['homeTeam']['displayName']
            game['home_team_abbr'] = event['spreads']['gameView']['homeTeam']['shortName']
            game['home_team_rank'] = event['spreads']['gameView']['homeTeam']['rank']
            game['away_team'] = event['spreads']['gameView']['awayTeam']['fullName']
            game['away_team_loc'] = event['spreads']['gameView']['awayTeam']['displayName']
            game['away_team_abbr'] = event['spreads']['gameView']['awayTeam']['shortName']
            game['away_team_rank'] = event['spreads']['gameView']['awayTeam']['rank']
            game['home_score'] = event['spreads']['gameView']['homeTeamScore']
            game['away_score'] = event['spreads']['gameView']['awayTeamScore']
            game['home_spread'] = {}
            game['home_spread_odds'] = {}
            game['away_spread'] = {}
            game['away_spread_odds'] = {}
            game['under_odds'] = {}
            game['over_odds'] = {}
            game['total'] = {}
            game['home_ml'] = {}
            game['away_ml'] = {}
            if 'spreads' in event:
                for line in event['spreads']['oddsViews']:
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
        self.games = games