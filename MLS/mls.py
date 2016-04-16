#!/usr/bin/python

import configparser
import json
import os
import re
from decimal import Decimal
from bs4 import BeautifulSoup
import pymysql
import requests

GAMES = {}
TEAMS = {}
db = None
config = None
date_regex = re.compile(".*matchcenter/(\d\d\d\d-\d\d-\d\d)-.*")
western_conf = {'Colorado Rapids': "COL",
                'FC Dallas': "DAL",
                'Houston Dynamo': "HOU",
                'LA Galaxy': 'LAG',
                'Portland Timbers': 'POR',
                'Real Salt Lake': 'RSL',
                'San Jose Earthquakes': 'SJQ',
                'Seattle Sounders FC': 'SEA',
                'Sporting Kansas City': 'SKC',
                'Vancouver Whitecaps FC': 'VAN'}
eastern_conf = {'Chicago Fire': 'CHI',
                'Columbus Crew SC': 'CMB',
                'D.C. United': 'DCU',
                'Montreal Impact': 'MTL',
                'New England Revolution': 'NEW',
                'New York City FC': 'NYC',
                'New York Red Bulls': 'NYR',
                'Orlando City SC': 'ORL',
                'Philadelphia Union': 'PHL',
                'Toronto FC': 'TOR'}
YEAR = 2016


class TeamEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.__dict__


class Team(object):
    def __init__(self, name, year):
        self.season = year
        if name in western_conf:
            self.conference = 'W'
            self.name = western_conf[name]
        else:
            self.conference = 'E'
            self.name = eastern_conf[name]
        self.games_played = 0
        self.games_left = 0
        self.points = 0
        self.goals_scored = 0
        self.goals_allowed = 0
        self.home_games_played = 0
        self.home_games_left = 0
        self.home_points = 0
        self.home_goals_scored = 0
        self.home_goals_allowed = 0
        self.road_games_played = 0
        self.road_games_left = 0
        self.road_points = 0
        self.road_goals_scored = 0
        self.road_goals_allowed = 0

    def project(self):
        ppg = 0
        if self.games_played:
            ppg = Decimal(self.points) / self.games_played
        points_to_go = ppg * self.games_left
        self.proj_points = (points_to_go) + self.points
        h_ppg = 0
        if self.home_games_played:
            h_ppg = Decimal(self.home_points) / self.home_games_played
        home_points_to_go = h_ppg * self.home_games_left
        self.proj_home_points = (home_points_to_go) + self.home_points
        r_ppg = 0
        if self.road_games_played:
            r_ppg = Decimal(self.road_points) / self.road_games_played
        road_points_to_go = r_ppg * self.road_games_left
        self.proj_road_points = (road_points_to_go) + self.road_points


def read_config():
    global config
    config = configparser.ConfigParser()
    config_file = os.path.join(os.path.dirname(__file__), "config.ini")
    config.read(config_file)
    return config


def init_db():
    global db
    user = config['mysql']['user']
    pwd = config['mysql']['pwd']
    host = config['mysql']['host']
    db_name = config['mysql']['db_name']
    db = pymysql.connect(host=host, passwd=pwd, user=user, db=db_name)
    return db


def build_cache():
    global GAMES
    cursor = db.cursor()
    cursor.execute('SELECT gameDate, homeTeam, awayTeam, homeScore, awayScore ',
                   'FROM fixtures WHERE YEAR(gamedate)=%s' % YEAR)
    for row in cursor.fetchall():
        game_key = "%s ~ %s ~ %s ~ %s ~ %s" % (row[0], row[1], row[2], row[3], row[4])
        GAMES[game_key] = "exists"


def get_games():
    url = "http://www.mlssoccer.com/schedule?month=all&year=%s&" % YEAR
    url += ("club=select&club_options=9&op=Update&form_id=mp7_schedule_hub_search_filters_form")
    req = requests.get(url)
    raw_src = req.text
    soup = BeautifulSoup(raw_src, "html.parser")

    for game in soup.findAll("li", {'class':['row_no_padding']}):
        try:
            home_line = game.find("div", attrs={"class": "home_club"})
            home_team = home_line.find("span", attrs={"class": "club_name"}).get_text().strip()
            away_line = game.find("div", attrs={"class": "vs_club"})
            away_team = away_line.find("span", attrs={"class": "club_name"}).get_text().strip()

            home_score = home_line.find("span", attrs={"class": "match_score"})
            if home_score is None:
                scores = [-1, -1]
            else:
                scores = [home_score.get_text()]
                scores.append(away_line.find("span", attrs={"class": "match_score"}).get_text())

            game_date = date_regex.findall(str(game))[0]

            insert_game(game_date, home_team, away_team, scores)
        except AttributeError:
            print(game)


def insert_game(game_date, home_team, away_team, scores):
    global GAMES
    game_key = "%s ~ %s ~ %s ~ %s ~ %s" % (game_date, home_team, away_team, scores[0], scores[1])
    if game_key in GAMES:
        return
    else:
        # insert into DB
        cursor = db.cursor()
        sql = "REPLACE INTO fixtures VALUES ('%s', '%s', '%s', %s, %s)" % (
                game_date, home_team, away_team, scores[0], scores[1])
        if cursor.execute('%s' % sql):
            cursor.close()
            db.commit()
            GAMES[game_key] = 'exists'
            return


def build_teams():
    for game in GAMES:
        game_info = game.split(' ~ ')
        home_score = int(game_info[3])
        road_score = int(game_info[4])
        if game_info[1] not in TEAMS:
            TEAMS[game_info[1]] = Team(game_info[1], YEAR)
        home_team = TEAMS[game_info[1]]
        if game_info[2] not in TEAMS:
            TEAMS[game_info[2]] = Team(game_info[2], YEAR)
        road_team = TEAMS[game_info[2]]
        if home_score < 0:
            home_team.games_left += 1
            road_team.games_left += 1
            home_team.home_games_left += 1
            road_team.road_games_left += 1
        else:
            home_team.games_played += 1
            home_team.home_games_played += 1
            home_team.goals_scored += home_score
            home_team.home_goals_scored += home_score
            home_team.goals_allowed += road_score
            home_team.home_goals_allowed += road_score
            road_team.games_played += 1
            road_team.road_games_played += 1
            road_team.goals_scored += road_score
            road_team.road_goals_scored += road_score
            road_team.goals_allowed += home_score
            road_team.road_goals_allowed += home_score

            if home_score > road_score:
                home_team.points += 3
                home_team.home_points += 3

            elif home_score < road_score:
                road_team.points += 3
                road_team.road_points += 3

            else:
                home_team.points += 1
                home_team.home_points += 1
                road_team.points += 1
                road_team.road_points += 1
    for team in TEAMS:
        TEAMS[team].project()


def compile_cache():
    cache_file = open('./mls_table.cache', 'w')
    output = '{ "year": {"' + str(YEAR) + '": {'
    for team in TEAMS:
        team_obj = TEAMS[team]
        output += '"' + team + '": '
        output += json.dumps(team_obj.__dict__, sort_keys=True, default=to_json)
        output += ","
    output = output[:-1] + '}}}'
    cache_file.write(output)
    cache_file.close()


def to_json(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    else:
        return str(obj)
    raise TypeError


read_config()
init_db()
get_games()
build_teams()
compile_cache()
