from datetime import datetime
import requests
import re
import json
import time
import calendar

headers = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
  "Accept": "application/json",
  "Content-Type": "application/json"
}

provider_mapping = {
    10: 'pinnacle',
    8: 'betonline',
    3: 'bookmaker',
    9: 'sportsbetting',
    20: 'betanyports',
    44: 'heritage',
    29: 'lowvig',
    38: 'justbet',
    16: 'gtbets',
    65: 'betus',
    92: 'everygame',
    28: 'intertops',
    83: 'betnow',
    84: 'bovada',
    82: 'bodog',
    15: 'mybookie',
    35: 'betcris',
    45: 'wynn',
    54: 'resorts',
    22: 'sugarhouse',
    18: '888sport',
    5: 'williamhill',
    36: 'unibet',
    78: 'fanduel',
    91: 'draftkings',
    123: 'consensus'
}

sport_dict = {"NBA": "nba-basketball",
              "NFL": "nfl-football",
              "NHL": "nhl-hockey",
              "MLB": "mlb-baseball",
              "NCAAB": "ncaa-basketball"}

def make_ordinal(n):
    try:
        n = int(n)
    except:
        return str(n).upper()
    suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    return str(n) + suffix

class Scoreboard:
    def __init__(self, sport='NBA', date="", current_line=True):
        self.games = []
        try:
            self.scrape_games(sport, date, current_line)
        except Exception as e:
            # print(f"SBR scraping failed: {e}")
            pass
            
        try:
            self.scrape_oddstrader(sport, date)
        except Exception as e:
            # print(f"Oddstrader scraping failed: {e}")
            pass

    def scrape_games(self, sport="NBA", date="", current_line=True):
        if date == "":
            date = datetime.today().strftime("%Y-%m-%d")
        _line = 'currentLine' if current_line else 'openingLine'

        spread_url = f"https://www.sportsbookreview.com/betting-odds/{sport_dict[sport]}/?date={date}"
        r = requests.get(spread_url, headers=headers)
        j = re.findall('__NEXT_DATA__" type="application/json">(.*?)</script>',r.text)
        if not j:
            return

        try:
            build_id = json.loads(j[0])['buildId']
            spreads_url = f"https://www.sportsbookreview.com/_next/data/{build_id}/betting-odds/{sport_dict[sport]}.json?league={sport_dict[sport]}&date={date}"
            spreads_json = requests.get(spreads_url, headers=headers).json()
            spreads_list = spreads_json['pageProps']['oddsTables'][0]['oddsTableModel']['gameRows']
            spreads = {g['gameView']['gameId']: g for g in spreads_list}
        except (IndexError, KeyError, TypeError):
            return

        try:
            moneyline_url = f"https://www.sportsbookreview.com/_next/data/{build_id}/betting-odds/{sport_dict[sport]}/money-line/full-game.json?league={sport_dict[sport]}&oddsType=money-line&oddsScope=full-game&date={date}"
            moneyline_json = requests.get(moneyline_url, headers=headers).json()
            moneylines_list = moneyline_json['pageProps']['oddsTables'][0]['oddsTableModel']['gameRows']
            moneylines = {g['gameView']['gameId']: g for g in moneylines_list}
        except (IndexError, KeyError, TypeError):
            moneylines = {}

        try:
            totals_url = f"https://www.sportsbookreview.com/_next/data/{build_id}/betting-odds/{sport_dict[sport]}/totals/full-game.json?league={sport_dict[sport]}&oddsType=totals&oddsScope=full-game&date={date}"
            totals_json = requests.get(totals_url, headers=headers).json()
            totals_list = totals_json['pageProps']['oddsTables'][0]['oddsTableModel']['gameRows']
            totals = {g['gameView']['gameId']: g for g in totals_list}
        except (IndexError, KeyError, TypeError):
            totals = {}

        all_stats = {
            game_id: {
                'spreads': spreads[game_id], 
                'moneylines': moneylines.get(game_id), 
                'totals': totals.get(game_id), 
            } for game_id in spreads.keys()
        }

        games = []
        for event in all_stats.values():
            game = {}
            game['source'] = 'sportsbookreview'
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
            
            home_score = event['spreads']['gameView']['homeTeamScore']
            away_score = event['spreads']['gameView']['awayTeamScore']
            if event['spreads'].get('liveScoreViews') and event['spreads']['liveScoreViews'].get('viewdata'):
                score_data = event['spreads']['liveScoreViews']['viewdata'].get('GameTeamScoreDataList')
                if score_data:
                    home_score = 0
                    away_score = 0
                    for s in score_data:
                        if s['isHomeTeam']:
                            home_score += s['Points']
                        else:
                            away_score += s['Points']
            
            game['home_score'] = home_score
            game['away_score'] = away_score
            game['home_spread'] = {}
            game['home_spread_odds'] = {}
            game['away_spread'] = {}
            game['away_spread_odds'] = {}
            game['under_odds'] = {}
            game['over_odds'] = {}
            game['total'] = {}
            game['home_ml'] = {}
            game['away_ml'] = {}
            if 'spreads' in event and event['spreads'].get('oddsViews'):
                for line in event['spreads']['oddsViews']:
                    if not line or not line.get(_line):
                        continue
                    game['home_spread'][line['sportsbook']] = line[_line].get('homeSpread')
                    game['home_spread_odds'][line['sportsbook']] = line[_line].get('homeOdds')
                    game['away_spread'][line['sportsbook']] = line[_line].get('awaySpread')
                    game['away_spread_odds'][line['sportsbook']] = line[_line].get('awayOdds')
            if 'totals' in event and event['totals'] and event['totals'].get('oddsViews'):
                for line in event['totals']['oddsViews']:
                    if not line or not line.get(_line):
                        continue
                    game['under_odds'][line['sportsbook']] = line[_line].get('underOdds')
                    game['over_odds'][line['sportsbook']] = line[_line].get('overOdds')
                    game['total'][line['sportsbook']] = line[_line].get('total')
            if 'moneylines' in event and event['moneylines'] and event['moneylines'].get('oddsViews'):
                for line in event['moneylines']['oddsViews']:
                    if not line or not line.get(_line):
                        continue
                    game['home_ml'][line['sportsbook']] = line[_line].get('homeOdds')
                    game['away_ml'][line['sportsbook']] = line[_line].get('awayOdds')
            games.append(game)
        self.games = games

    def scrape_oddstrader(self, sport="NBA", date=""):
        if date == "":
            date_ts = int((calendar.timegm(time.gmtime()) - 86400) * 1000)
        else:
            dt = datetime.strptime(date, "%Y-%m-%d")
            date_ts = int(calendar.timegm(dt.utctimetuple()) * 1000)

        lids = {"NBA": 5, "NFL": 16, "NHL": 7, "MLB": 3, "NCAAB": 14}
        spids = {"NBA": 5, "NFL": 4, "NHL": 6, "MLB": 3, "NCAAB": 5}
        mtids = {"NBA": [401, 402, 83], "NFL": [401, 402, 83], "NHL": [125, 401, 412], "MLB": [83, 401, 402], "NCAAB": [401, 402, 83]}

        if sport not in lids:
            return

        lid = lids[sport]
        spid = spids[sport]
        mtid = mtids[sport]

        query = '{+eventsByDateByLeagueGroup(+leagueGroups:+[{+mtid:+' + str(mtid) + ',+lid:+' + str(lid) + ',+spid:+' + str(spid) + '+}],+showEmptyEvents:+true,+marketTypeLayout:+"PARTICIPANTS",+ic:+false,+startDate:+' + str(date_ts) + ',+timezoneOffset:+-4,+nof:+true,+hl:+true,+sort:+{by:+["lid",+"dt",+"des"],+order:+ASC}+)+{+events+{+eid+lid+spid+des+dt+es+rid+ic+ven+tvs+cit+cou+st+sta+hl+seid+consensus+{+eid+mtid+bb+boid+partid+sbid+paid+lineid+wag+perc+vol+tvol+wb+}+plays(pgid:+2,+limitLastSeq:+3)+{+eid+sqid+siid+gid+nam+val+tim+}+scores+{+partid+val+eid+pn+sequence+}+participants+{+eid+partid+psid+ih+rot+tr+sppil+startingPitcher+{+fn+lnam+}+source+{+...+on+Player+{+pid+fn+lnam+}+...+on+Team+{+tmid+lid+nam+nn+sn+abbr+cit+}+...+on+ParticipantGroup+{+partgid+nam+lid+participants+{+eid+partid+psid+ih+rot+source+{+...+on+Player+{+pid+fn+lnam+}+...+on+Team+{+tmid+lid+nam+nn+sn+abbr+cit+}+}+}+}+}+}+marketTypes+{+mtid+spid+nam+des+settings+{+sitid+did+alias+layout+format+template+sort+url+}+}+bettingOptions+{+boid+nam+mtid+spid+partid+}+currentLines(paid:+[20,3,10,8,9,44,29,38,16,65,92,28,83,84,82,15,35,45,54,22,18,5,36,78,91,123])+openingLines+eventGroup+{+egid+nam+}+statistics(sgid:+3)+{+val+eid+nam+partid+pid+typ+siid+sequence+}+league+{+lid+nam+rid+spid+sn+settings+{+alias+rotation+ord+shortnamebreakpoint+}+}+}+maxSequences+{+events:+eventsMaxSequence+scores:+scoresMaxSequence+currentLines:+linesMaxSequence+statistics:+statisticsMaxSequence+plays:+playsMaxSequence+}+}+}'
        url = f'https://www.oddstrader.com/odds-v2/odds-v2-service?query={query}'
        
        r = requests.get(url, headers=headers)
        data = r.json()
        events = data['data']['eventsByDateByLeagueGroup']['events']
        
        new_games = []
        for event in events:
            game = {}
            game['source'] = 'oddstrader'
            game['date'] = datetime.utcfromtimestamp(event['dt'] / 1000.0).strftime('%Y-%m-%dT%H:%M:%S+00:00')
            game['status'] = event['es']
            
            home_id = 0
            away_id = 0
            for participant in event['participants']:
                if participant['ih']:
                    home_id = participant['source']['tmid']
                    game['home_team'] = participant['source']['nam']
                    game['home_team_loc'] = participant['source'].get('cit', '')
                    game['home_team_abbr'] = participant['source']['abbr']
                    game['home_team_rank'] = participant['tr']
                else:
                    away_id = participant['source']['tmid']
                    game['away_team'] = participant['source']['nam']
                    game['away_team_loc'] = participant['source'].get('cit', '')
                    game['away_team_abbr'] = participant['source']['abbr']
                    game['away_team_rank'] = participant['tr']
            
            if 'home_team' not in game or 'away_team' not in game:
                continue

            home_score = 0
            away_score = 0
            for score in event['scores']:
                if score['partid'] == home_id:
                    home_score += int(score['val'])
                elif score['partid'] == away_id:
                    away_score += int(score['val'])
            game['home_score'] = home_score
            game['away_score'] = away_score
            
            game['home_spread'] = {}
            game['home_spread_odds'] = {}
            game['away_spread'] = {}
            game['away_spread_odds'] = {}
            game['under_odds'] = {}
            game['over_odds'] = {}
            game['total'] = {}
            game['home_ml'] = {}
            game['away_ml'] = {}

            if event.get('currentLines'):
                for line in event['currentLines']:
                    book = provider_mapping.get(line['paid'], f"unknown_{line['paid']}")
                    mtid_val = line['mtid']
                    if mtid_val == 401: # spread
                        if line['partid'] == home_id:
                            game['home_spread'][book] = line['adj']
                            game['home_spread_odds'][book] = line['ap']
                        elif line['partid'] == away_id:
                            game['away_spread'][book] = line['adj']
                            game['away_spread_odds'][book] = line['ap']
                    elif mtid_val in [402, 412]: # over/under
                        if line['partid'] == 15144: # under
                            game['under_odds'][book] = line['ap']
                        elif line['partid'] == 15143: # over
                            game['over_odds'][book] = line['ap']
                        
                        game['total'][book] = line['adj']
                    elif mtid_val in [83, 125]: # moneyline
                        if line['partid'] == home_id:
                            game['home_ml'][book] = line['ap']
                        elif line['partid'] == away_id:
                            game['away_ml'][book] = line['ap']
            
            # Additional status info from plays/statistics if in-progress
            if event['es'] == 'in-progress':
                time_val = qtr = ""
                for play in event['plays']:
                    if time_val == "" and play['nam'] in ["event_clock", "event-clock"]:
                        time_val = play['val']
                    if qtr == "" and play['nam'] in ["last-play-half", "last-play-period", "last-play-quarter"]:
                        qtr = make_ordinal(play['val'])
                if time_val != "" and qtr != "":
                    game['status'] = qtr + ' ' + time_val

            # Merge with existing games from SBR if possible
            found = False
            for existing_game in self.games:
                def normalize(name):
                    return name.lower().replace('.', '').replace(' ', '').replace('losangeles', 'la').replace('stlouis', 'stl')
                
                ot_home = normalize(game['home_team'])
                sbr_home = normalize(existing_game['home_team'])
                ot_away = normalize(game['away_team'])
                sbr_away = normalize(existing_game['away_team'])
                
                if (ot_home in sbr_home or sbr_home in ot_home) and \
                   (ot_away in sbr_away or sbr_away in ot_away):
                    # Prefer Oddstrader for status and scores if in-progress or final
                    if game['status'] != 'scheduled' or existing_game['status'] == '':
                        existing_game['status'] = game['status']
                        existing_game['home_score'] = game['home_score']
                        existing_game['away_score'] = game['away_score']
                    
                    # Also merge odds if not present in SBR game
                    for book, val in game['home_spread'].items():
                        if book not in existing_game['home_spread']:
                            existing_game['home_spread'][book] = val
                            existing_game['home_spread_odds'][book] = game['home_spread_odds'].get(book)
                    for book, val in game['away_spread'].items():
                        if book not in existing_game['away_spread']:
                            existing_game['away_spread'][book] = val
                            existing_game['away_spread_odds'][book] = game['away_spread_odds'].get(book)
                    for book, val in game['total'].items():
                        if book not in existing_game['total']:
                            existing_game['total'][book] = val
                            existing_game['under_odds'][book] = game['under_odds'].get(book)
                            existing_game['over_odds'][book] = game['over_odds'].get(book)
                    for book, val in game['home_ml'].items():
                        if book not in existing_game['home_ml']:
                            existing_game['home_ml'][book] = val
                    for book, val in game['away_ml'].items():
                        if book not in existing_game['away_ml']:
                            existing_game['away_ml'][book] = val
                    
                    found = True
                    break
            
            if not found:
                new_games.append(game)
        
        self.games.extend(new_games)
